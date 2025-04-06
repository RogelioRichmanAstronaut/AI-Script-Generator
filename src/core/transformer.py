import os
import logging
import json
import time
from typing import List, Dict, Optional, Callable, Any
import openai
from src.utils.text_processor import TextProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordCountError(Exception):
    """Raised when word count requirements are not met"""
    pass

class TranscriptTransformer:
    """Transforms conversational transcripts into teaching material using LLM"""
    
    MAX_RETRIES = 3  # Initial retries for content generation
    EXTENDED_RETRIES = 3  # Additional retries with longer waits
    EXTENDED_RETRY_DELAYS = [5, 10, 15]  # Wait times in seconds for extended retries
    CHUNK_SIZE = 6000  # Target words per chunk
    LARGE_DEVIATION_THRESHOLD = 0.20  # 20% maximum deviation
    MAX_TOKENS = 64000  # Nuevo límite absoluto basado en 64k tokens de salida
    
    def __init__(self, use_gemini: bool = True, use_thinking_model: bool = False):
        """Initialize the transformer with selected LLM client"""
        self.text_processor = TextProcessor()
        self.use_gemini = use_gemini
        # self.use_thinking_model = use_thinking_model # No longer needed for model selection
        
        if use_gemini:
            logger.info("Initializing with Gemini API")
            # Always use the new pro preview model
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('GEMINI_API_KEY'),
                # Assuming the base URL for pro preview is the same as beta, adjust if needed
                base_url="https://generativelanguage.googleapis.com/v1beta" 
            )
            self.model_name = "gemini-2.0-flash-thinking-exp-01-21"
            logger.debug(f"Using model: {self.model_name}")
            
        # Removed the separate block for use_thinking_model as it's now the default gemini case
        # elif use_gemini: # This block is merged above
        #     logger.info("Initializing with Gemini API")
        #     self.openai_client = openai.OpenAI(...)
        #     self.model_name = "gemini-2.0-flash-exp" 

        else: # OpenAI case remains the same
            logger.info("Initializing with OpenAI API")
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            self.model_name = "gpt-3.5-turbo"
            logger.debug(f"Using model: {self.model_name}")
        
        # Target word counts
        self.words_per_minute = 130  # Average speaking rate
        
    def _api_call_with_enhanced_retries(self, call_func: Callable[[], Any]) -> Any:
        """
        Wrapper function for API calls with enhanced retry logic
        
        Args:
            call_func: Function that makes the actual API call
            
        Returns:
            The result of the successful API call
            
        Raises:
            Exception: If all retries fail
        """
        # Initial retries (already handled by openai client)
        try:
            return call_func()
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a quota error (429)
            if "429" in error_str or "Too Many Requests" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                logger.warning(f"Quota error detected: {error_str}")
                logger.info(f"Starting extended retries with longer waits...")
                
                # Extended retries with longer waits
                for i in range(self.EXTENDED_RETRIES):
                    wait_time = self.EXTENDED_RETRY_DELAYS[i]
                    logger.info(f"Extended retry {i+1}/{self.EXTENDED_RETRIES}: Waiting {wait_time} seconds before retry")
                    time.sleep(wait_time)
                    
                    try:
                        return call_func()
                    except Exception as retry_error:
                        # If last retry, re-raise
                        if i == self.EXTENDED_RETRIES - 1:
                            logger.error(f"All extended retries failed: {str(retry_error)}")
                            raise
                        # Otherwise log and continue to next retry
                        logger.warning(f"Extended retry {i+1} failed: {str(retry_error)}")
            else:
                # Not a quota error, re-raise
                raise
        
    def _validate_word_count(self, total_words: int, target_words: int, min_words: int, max_words: int) -> None:
        """Validate word count with flexible thresholds and log warnings/errors"""
        deviation = abs(total_words - target_words) / target_words
        
        if deviation > self.LARGE_DEVIATION_THRESHOLD:
            logger.error(
                f"Word count {total_words} significantly outside target range "
                f"({min_words}-{max_words}). Deviation: {deviation:.2%}"
            )
        elif total_words < min_words or total_words > max_words:
            logger.warning(
                f"Word count {total_words} slightly outside target range "
                f"({min_words}-{max_words}). Deviation: {deviation:.2%}"
            )
            
    def transform_to_lecture(self, 
                             text: str,
                             target_duration: int = 30,
                             include_examples: bool = True,
                             initial_prompt: Optional[str] = None) -> str:
        """
        Transform input text into a structured teaching transcript
        
        Args:
            text: Input transcript text
            target_duration: Target lecture duration in minutes
            include_examples: Whether to include practical examples
            initial_prompt: Additional user instructions to guide the generation
            
        Returns:
            str: Generated teaching transcript, regardless of word count validation
        """
        logger.info(f"Starting transformation for {target_duration} minute lecture")
        
        # Clean and preprocess text
        cleaned_text = self.text_processor.clean_text(text)
        input_words = self.text_processor.count_words(cleaned_text)
        logger.info(f"Input text cleaned. Word count: {input_words}")
        
        # Calculate target word count
        target_words = self.words_per_minute * target_duration
        min_words = int(target_words * 0.95)  # Minimum 95% of target
        max_words = int(target_words * 1.05)  # Maximum 105% of target
        
        logger.info(f"Target word count: {target_words} (min: {min_words}, max: {max_words})")
        
        # Generate detailed lecture structure with topics
        structure_data = self._generate_detailed_structure(
            text=cleaned_text,
            target_duration=target_duration,
            initial_prompt=initial_prompt
        )
        logger.info("Detailed lecture structure generated")
        logger.info(f"Topics identified: {[t['title'] for t in structure_data['topics']]}")
        
        # Calculate section word counts
        section_words = {
            'intro': int(target_words * 0.1),
            'main': int(target_words * 0.7),
            'practical': int(target_words * 0.15),
            'summary': int(target_words * 0.05)
        }
        
        try:
            logger.info("Generating content by sections with topic tracking")
            
            # Introduction with learning objectives and topic preview
            intro = self._generate_section(
                'introduction',
                structure_data,
                cleaned_text,
                section_words['intro'],
                include_examples,
                is_first=True,
                initial_prompt=initial_prompt
            )
            intro_words = self.text_processor.count_words(intro)
            logger.info(f"Introduction generated: {intro_words} words")
            
            # Track context for coherence
            context = {
                'current_section': 'introduction',
                'covered_topics': [],
                'pending_topics': [t['title'] for t in structure_data['topics']],
                'key_terms': set(),
                'current_narrative': intro[-1000:],  # Last 1000 words for context
                'learning_objectives': structure_data['learning_objectives']
            }
            
            # Main content with topic progression
            main_content = self._generate_main_content(
                structure_data,
                cleaned_text,
                section_words['main'],
                include_examples,
                context,
                initial_prompt=initial_prompt
            )
            main_words = self.text_processor.count_words(main_content)
            logger.info(f"Main content generated: {main_words} words")
            
            # Update context after main content
            context['current_section'] = 'main'
            context['current_narrative'] = main_content[-1000:]
            
            # Practical applications tied to main topics
            practical = self._generate_section(
                'practical',
                structure_data,
                cleaned_text,
                section_words['practical'],
                include_examples,
                context=context,
                initial_prompt=initial_prompt
            )
            practical_words = self.text_processor.count_words(practical)
            logger.info(f"Practical section generated: {practical_words} words")
            
            # Update context for summary
            context['current_section'] = 'practical'
            context['current_narrative'] = practical[-500:]
            
            # Summary with topic reinforcement
            summary = self._generate_section(
                'summary',
                structure_data,
                cleaned_text,
                section_words['summary'],
                include_examples,
                is_last=True,
                context=context,
                initial_prompt=initial_prompt
            )
            summary_words = self.text_processor.count_words(summary)
            logger.info(f"Summary generated: {summary_words} words")
            
            # Combine all sections
            full_content = f"{intro}\n\n{main_content}\n\n{practical}\n\n{summary}"
            total_words = self.text_processor.count_words(full_content)
            logger.info(f"Total content generated: {total_words} words")
            
            # Log warnings/errors but don't raise exceptions
            self._validate_word_count(total_words, target_words, min_words, max_words)
            
            # Validate coherence
            self._validate_coherence(full_content, structure_data)
            logger.info("Content coherence validated")
            
            return full_content
            
        except Exception as e:
            logger.error(f"Error during content generation: {str(e)}")
            # If we have partial content, return it
            if 'full_content' in locals():
                logger.warning("Returning partial content despite errors")
                return full_content
            raise  # Re-raise only if we have no content at all
            
    def _generate_detailed_structure(self,
                                     text: str,
                                     target_duration: int,
                                     initial_prompt: Optional[str] = None) -> Dict:
        """Generate detailed lecture structure with topics and objectives"""
        logger.info("Generating detailed lecture structure")
        
        user_instructions = f"\nAdditional user instructions:\n{initial_prompt}\n" if initial_prompt else ""
        
        prompt = f"""
        You are an expert educator creating a detailed lecture outline.
        {user_instructions}
        Analyze this transcript and create a structured JSON output with the following:
        
        1. Title of the lecture
        2. 3-5 clear learning objectives
        3. 3-4 main topics, each with:
           - Title
           - Key concepts
           - Subtopics
           - Time allocation (in minutes)
           - Connection to learning objectives
        4. Practical application ideas
        5. Key terms to track
        
        IMPORTANT: Response MUST be valid JSON. Format exactly like this, with no additional text:
        {{
            "title": "string",
            "learning_objectives": ["string"],
            "topics": [
                {{
                    "title": "string",
                    "key_concepts": ["string"],
                    "subtopics": ["string"],
                    "duration_minutes": number,
                    "objective_links": [number]
                }}
            ],
            "practical_applications": ["string"],
            "key_terms": ["string"]
        }}
        
        Target duration: {target_duration} minutes
        
        Transcript excerpt:
        {text[:2000]}
        """
        
        try:
            # Common parameters
            params = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are an expert educator. Output ONLY valid JSON, no other text."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": self.MAX_TOKENS
            }
            
            # Use the enhanced retry wrapper for API call
            def api_call():
                return self.openai_client.chat.completions.create(**params)
                
            response = self._api_call_with_enhanced_retries(api_call)
            
            # -- Start Defensive Checks --
            content = None
            if response and response.choices:
                if len(response.choices) > 0:
                    choice = response.choices[0]
                    if choice and choice.message:
                        if choice.message.content:
                            content = choice.message.content.strip()
                        else:
                            logger.warning(f"API response for structure had null content.")
                    else:
                         logger.warning(f"API response for structure had null message in choice.")
                else:
                    logger.warning(f"API response for structure had empty choices list.")
            else:
                logger.warning(f"API response for structure was null or had no choices.")
            # -- End Defensive Checks --
            
            # If content is still None after checks, use fallback
            if content is None:
                 logger.error(f"Failed to get valid content for structure after API call and checks.")
                 # Provide a minimal fallback content to avoid complete failure
                 content = f"Lecture on Transcript Topic\n\nWe apologize, but there was an error generating the structure for this lecture."
            
            try:
                structure_data = json.loads(content)
                logger.info("Structure data parsed successfully")
                return structure_data
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON directly: {str(e)}")
                
                # Try to extract JSON if it's wrapped in other text
                import re
                json_match = re.search(r'({[\s\S]*})', content)
                if json_match:
                    try:
                        structure_data = json.loads(json_match.group(1))
                        logger.info("Structure data extracted and parsed successfully")
                        return structure_data
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse extracted JSON")
                
                # If both attempts fail, use fallback structure
                logger.warning("Using fallback structure")
                return self._generate_fallback_structure(text, target_duration)
                
        except Exception as e:
            logger.error(f"Error generating structure: {str(e)}")
            # Fallback in case of any error
            return self._generate_fallback_structure(text, target_duration)
            
    def _generate_fallback_structure(self, text: str, target_duration: int) -> Dict:
        """Generate a simplified fallback structure in case of parsing failures"""
        logger.info("Generating fallback structure")
        
        params = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are an expert educator. Output ONLY valid JSON, no other text."},
                {"role": "user", "content": f"""
                Create a simplified lecture outline based on this transcript.
                Format as JSON with: 
                - title
                - 3 learning objectives
                - 2 main topics with title, key concepts, subtopics
                - 2 practical applications
                - 3 key terms
                
                Target duration: {target_duration} minutes
                
                Transcript excerpt:
                {text[:2000]}
                """}
            ],
            "temperature": 0.5,
            "max_tokens": 2000
        }
        
        try:
            # Use the enhanced retry wrapper for API call
            def api_call():
                return self.openai_client.chat.completions.create(**params)
                
            response = self._api_call_with_enhanced_retries(api_call)
            
            # -- Start Defensive Checks --
            content = None
            if response and response.choices:
                if len(response.choices) > 0:
                    choice = response.choices[0]
                    if choice and choice.message:
                        if choice.message.content:
                            content = choice.message.content.strip()
                        else:
                            logger.warning(f"API response for fallback had null content.")
                    else:
                         logger.warning(f"API response for fallback had null message in choice.")
                else:
                    logger.warning(f"API response for fallback had empty choices list.")
            else:
                logger.warning(f"API response for fallback was null or had no choices.")
            # -- End Defensive Checks --
            
            # If content is still None after checks, use fallback
            if content is None:
                 logger.error(f"Failed to get valid content for fallback after API call and checks.")
                 # Provide a minimal fallback content to avoid complete failure
                 content = f"Lecture on Transcript Topic\n\nWe apologize, but there was an error generating the structure for this lecture."
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Last resort fallback if everything fails
                return {
                    "title": "Lecture on Transcript Topic",
                    "learning_objectives": ["Understand key concepts", "Apply knowledge", "Evaluate outcomes"],
                    "topics": [
                        {
                            "title": "Main Topic 1",
                            "key_concepts": ["Concept 1", "Concept 2"],
                            "subtopics": ["Subtopic 1", "Subtopic 2"],
                            "duration_minutes": target_duration // 2,
                            "objective_links": [1, 2]
                        },
                        {
                            "title": "Main Topic 2",
                            "key_concepts": ["Concept 3", "Concept 4"],
                            "subtopics": ["Subtopic 3", "Subtopic 4"],
                            "duration_minutes": target_duration // 2,
                            "objective_links": [2, 3]
                        }
                    ],
                    "practical_applications": ["Application 1", "Application 2"],
                    "key_terms": ["Term 1", "Term 2", "Term 3"]
                }
        except Exception as e:
            logger.error(f"Error generating fallback structure: {str(e)}")
            # Hardcoded last resort fallback
            return {
                "title": "Lecture on Transcript Topic",
                "learning_objectives": ["Understand key concepts", "Apply knowledge", "Evaluate outcomes"],
                "topics": [
                    {
                        "title": "Main Topic 1",
                        "key_concepts": ["Concept 1", "Concept 2"],
                        "subtopics": ["Subtopic 1", "Subtopic 2"],
                        "duration_minutes": target_duration // 2,
                        "objective_links": [1, 2]
                    },
                    {
                        "title": "Main Topic 2",
                        "key_concepts": ["Concept 3", "Concept 4"],
                        "subtopics": ["Subtopic 3", "Subtopic 4"],
                        "duration_minutes": target_duration // 2,
                        "objective_links": [2, 3]
                    }
                ],
                "practical_applications": ["Application 1", "Application 2"],
                "key_terms": ["Term 1", "Term 2", "Term 3"]
            }
        
    def _generate_section(self,
                         section_type: str,
                         structure_data: Dict,
                         original_text: str,
                         target_words: int,
                         include_examples: bool,
                         context: Dict = None,
                         is_first: bool = False,
                         is_last: bool = False,
                         initial_prompt: Optional[str] = None) -> str:
        """Generate a specific section of the lecture"""
        logger.info(f"Generating {section_type} section (target: {target_words} words)")
        
        # Calculate timing markers
        if section_type == 'introduction':
            time_marker = '[00:00]'
        elif section_type == 'summary':
            duration_mins = sum(topic.get('duration_minutes', 5) for topic in structure_data['topics'])
            # Asegurar que duration_mins es un entero y nunca menor a 5
            adjusted_mins = max(5, int(duration_mins - 5))
            time_marker = f'[{adjusted_mins:02d}:00]'
        else:
            # For other sections, use appropriate time markers
            time_marker = '[XX:XX]'  # Will be replaced within the prompt
        
        user_instructions = f"\nAdditional user instructions:\n{initial_prompt}\n" if initial_prompt else ""
        
        # Base prompt with context-specific formatting
        prompt = f"""
        You are creating a {section_type} section for a {time_marker} teaching lecture on "{structure_data['title']}".
        {user_instructions}
        Target word count: {target_words} words (very important)
        
        Learning objectives:
        {', '.join(structure_data['learning_objectives'])}
        
        Key terms:
        {', '.join(structure_data['key_terms'])}
        
        Original source:
        {original_text[:500]}...
        """
        
        # Section-specific instructions
        if section_type == 'introduction':
            prompt += """
            - Start with an engaging hook
            - Present clear learning objectives
            - Preview main topics
            - Set expectations for the lecture
            """
        elif section_type == 'main':
            prompt += f"""
            Discuss one main topic in depth.
            
            Topic: {context['current_topic']['title']}
            Key concepts: {', '.join(context['current_topic']['key_concepts'])}
            Subtopics: {', '.join(context['current_topic']['subtopics'])}
            
            - Start with appropriate time marker
            - Explain key concepts clearly
            - Include real-world examples
            - Connect to learning objectives
            - Use appropriate time markers within the section
            """
        elif section_type == 'practical':
            prompt += f"""
            Create a practical applications section with:
            
            - Start with appropriate time marker
            - 2-3 practical examples or case studies
            - Clear connections to the main topics
            - Interactive elements (questions, exercises)
            
            Practical applications to cover:
            {', '.join(structure_data['practical_applications'])}
            """
        elif section_type == 'summary':
            prompt += """
            Create a concise summary:
            
            - Start with appropriate time marker
            - Reinforce key learning points
            - Brief recap of main topics
            - Call to action or follow-up suggestions
            """
        
        # Context-specific content
        if context:
            prompt += f"""
            
            Previously covered topics:
            {', '.join(context['covered_topics'])}
            
            Pending topics:
            {', '.join(context['pending_topics'])}
            
            Recent narrative context:
            {context['current_narrative']}
            """
        
        # First/last section specific instructions
        if is_first:
            prompt += """
            
            This is the FIRST section of the lecture. Make it engaging and set the tone.
            """
        elif is_last:
            prompt += """
            
            This is the FINAL section of the lecture. Ensure proper closure and reinforcement.
            """
            
        # Add section-specific time markers for formatted output
        if section_type != 'introduction':
            prompt += """
            
            IMPORTANT: Include appropriate time markers [MM:SS] throughout the section.
            """
            
        try:
            # Prepare API call parameters
            params = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are an expert educator creating a teaching script."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": self._calculate_max_tokens(section_type, target_words)
            }
            
            # Use the enhanced retry wrapper for API call
            def api_call():
                return self.openai_client.chat.completions.create(**params)
                
            response = self._api_call_with_enhanced_retries(api_call)
            
            # -- Start Defensive Checks --
            content = None
            if response and response.choices:
                if len(response.choices) > 0:
                    choice = response.choices[0]
                    if choice and choice.message:
                        if choice.message.content:
                            content = choice.message.content.strip()
                        else:
                            logger.warning(f"API response for {section_type} had null content.")
                    else:
                         logger.warning(f"API response for {section_type} had null message in choice.")
                else:
                    logger.warning(f"API response for {section_type} had empty choices list.")
            else:
                logger.warning(f"API response for {section_type} was null or had no choices.")
            # -- End Defensive Checks --
            
            # If content is still None after checks, use fallback
            if content is None:
                 logger.error(f"Failed to get valid content for {section_type} after API call and checks.")
                 # Provide a minimal fallback content to avoid complete failure
                 content = f"{time_marker} {section_type.capitalize()} (Error retrieving generated content)\n\nWe apologize, but there was an error generating the content for this section."
            
            # Validate output length
            content_words = self.text_processor.count_words(content)
            logger.info(f"Section generated: {content_words} words")
            
            return content
            
        except Exception as e:
            logger.error(f"Error during content generation: {str(e)}")
            # Provide a minimal fallback content to avoid complete failure
            return f"{time_marker} {section_type.capitalize()} (Error during generation)\n\nWe apologize, but there was an error generating this section."
        
    def _calculate_max_tokens(self, section_type: str, target_words: int) -> int:
        """Calculate appropriate max_tokens based on section and model"""
        # 1 token ≈ 4 caracteres (1 palabra ≈ 1.33 tokens)
        base_tokens = int(target_words * 1.5)  # Margen para formato
        
        # Límites para otros modelos
        return min(base_tokens + 1000, self.MAX_TOKENS)
        
    def _generate_main_content(self,
                             structure_data: Dict,
                             original_text: str,
                             target_words: int,
                             include_examples: bool,
                             context: Dict,
                             initial_prompt: Optional[str] = None) -> str:
        """Generate main content with topic progression"""
        logger.info(f"Generating main content (target: {target_words} words)")
        
        # Calculate words per topic based on their duration ratios
        total_duration = sum(t['duration_minutes'] for t in structure_data['topics'])
        # Avoid division by zero
        total_duration = total_duration if total_duration > 0 else 1
        
        topic_words = {}
        
        for topic in structure_data['topics']:
            ratio = topic['duration_minutes'] / total_duration
            topic_words[topic['title']] = int(target_words * ratio)
            
        logger.info(f"Topic word allocations: {topic_words}")
        
        # Generate content for each topic
        topic_contents = []
        
        for topic in structure_data['topics']:
            topic_target = topic_words[topic['title']]
            
            # Update context for topic
            context['current_topic'] = topic
            if topic['title'] in context['pending_topics']:
                context['covered_topics'].append(topic['title'])
                context['pending_topics'].remove(topic['title'])
            context['key_terms'].update(topic['key_concepts'])
            
            # Generate topic content
            topic_content = self._generate_section(
                f"main_topic_{topic['title']}",
                structure_data,
                original_text,
                topic_target,
                include_examples,
                context=context,
                initial_prompt=initial_prompt
            )
            
            topic_contents.append(topic_content)
            context['current_narrative'] = topic_content[-1000:]
            
        return "\n\n".join(topic_contents)
        
    def _validate_coherence(self, content: str, structure_data: Dict):
        """Validate content coherence against structure"""
        logger.info("Validating content coherence")
        
        # Check for learning objectives
        for objective in structure_data['learning_objectives']:
            if not any(term.lower() in content.lower() for term in objective.split()):
                logger.warning(f"Learning objective not well covered: {objective}")
                
        # Check for key terms
        for term in structure_data['key_terms']:
            if content.lower().count(term.lower()) < 2:
                logger.warning(f"Key term underutilized: {term}")
                
        # Check topic coverage
        for topic in structure_data['topics']:
            if not any(concept.lower() in content.lower() for concept in topic['key_concepts']):
                logger.warning(f"Topic concepts not well covered: {topic['title']}")
                
        logger.info("Coherence validation complete") 