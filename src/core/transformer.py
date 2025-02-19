import os
import logging
import json
from typing import List, Dict, Optional
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
    
    MAX_RETRIES = 3  # Maximum retries for content generation
    CHUNK_SIZE = 6000  # Target words per chunk
    LARGE_DEVIATION_THRESHOLD = 0.20  # 20% maximum deviation
    MAX_TOKENS = 64000  # Nuevo límite absoluto basado en 64k tokens de salida
    
    def __init__(self, use_gemini: bool = True, use_thinking_model: bool = False):
        """Initialize the transformer with selected LLM client"""
        self.text_processor = TextProcessor()
        self.use_gemini = use_gemini
        self.use_thinking_model = use_thinking_model
        
        if use_thinking_model:
            if not use_gemini:
                raise ValueError("Thinking model requires use_gemini=True")
                
            logger.info("Initializing with Gemini Flash Thinking API")
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('GEMINI_API_KEY'),
                base_url="https://generativelanguage.googleapis.com/v1alpha"
            )
            self.model_name = "gemini-2.0-flash-thinking-exp-01-21"
        elif use_gemini:
            logger.info("Initializing with Gemini API")
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('GEMINI_API_KEY'),
                base_url="https://generativelanguage.googleapis.com/v1beta"
            )
            self.model_name = "gemini-2.0-flash-exp"
        else:
            logger.info("Initializing with OpenAI API")
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            self.model_name = "gpt-3.5-turbo"
        
        # Target word counts
        self.words_per_minute = 130  # Average speaking rate
        
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
                "max_tokens": self.MAX_TOKENS if self.use_thinking_model else 4000
            }
            
            # Add thinking config if using experimental model
            if self.use_thinking_model:
                params["extra_body"] = {
                    "thinking_config": {
                        "include_thoughts": True
                    }
                }

            response = self.openai_client.chat.completions.create(**params)
            content = response.choices[0].message.content.strip()
            logger.debug(f"Raw structure response: {content}")
            
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
            return self._generate_fallback_structure(text, target_duration)
            
    def _generate_fallback_structure(self, text: str, target_duration: int) -> Dict:
        """Generate a basic fallback structure when JSON parsing fails"""
        logger.info("Generating fallback structure")
        
        # Generate a simpler structure prompt
        prompt = f"""
        Analyze this text and provide:
        1. A title (one line)
        2. Three learning objectives (one per line)
        3. Three main topics (one per line)
        4. Three key terms (one per line)
        
        Text: {text[:1000]}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert educator. Provide concise, line-by-line responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            lines = response.choices[0].message.content.strip().split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            # Extract components from lines
            title = lines[0] if lines else "Lecture"
            objectives = [obj for obj in lines[1:4] if obj][:3]
            topics = [topic for topic in lines[4:7] if topic][:3]
            terms = [term for term in lines[7:10] if term][:3]
            
            # Calculate minutes per topic
            main_time = int(target_duration * 0.7)  # 70% for main content
            topic_minutes = main_time // len(topics) if topics else main_time
            
            # Create fallback structure
            return {
                "title": title,
                "learning_objectives": objectives,
                "topics": [
                    {
                        "title": topic,
                        "key_concepts": [topic],  # Use topic as key concept
                        "subtopics": ["Overview", "Details", "Examples"],
                        "duration_minutes": topic_minutes,
                        "objective_links": [1]  # Link to first objective
                    }
                    for topic in topics
                ],
                "practical_applications": [
                    "Real-world application example",
                    "Interactive exercise",
                    "Case study"
                ],
                "key_terms": terms
            }
            
        except Exception as e:
            logger.error(f"Error generating fallback structure: {str(e)}")
            # Return minimal valid structure
            return {
                "title": "Lecture Overview",
                "learning_objectives": ["Understand key concepts", "Apply knowledge", "Analyze examples"],
                "topics": [
                    {
                        "title": "Main Topic",
                        "key_concepts": ["Core concept"],
                        "subtopics": ["Overview"],
                        "duration_minutes": target_duration // 2,
                        "objective_links": [1]
                    }
                ],
                "practical_applications": ["Practical example"],
                "key_terms": ["Key term"]
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
        """Generate content for a specific section with coherence tracking"""
        logger.info(f"Generating {section_type} section (target: {target_words} words)")
        
        user_instructions = f"\nUser's guiding instructions:\n{initial_prompt}\n" if initial_prompt else ""
        
        # Base prompt with structure
        prompt = f"""
        You are an expert educator creating a detailed lecture transcript.
        {user_instructions}
        Generate the {section_type} section with EXACTLY {target_words} words.
        
        Lecture Title: {structure_data['title']}
        Learning Objectives: {', '.join(structure_data['learning_objectives'])}
        
        Current section purpose:
        """
        
        # Add section-specific guidance
        if section_type == 'introduction':
            prompt += """
            - Start with an engaging hook
            - Present clear learning objectives
            - Preview main topics
            - Set expectations for the lecture
            """
        elif section_type == 'main':
            prompt += f"""
            - Cover these topics: {[t['title'] for t in structure_data['topics']]}
            - Build progressively on concepts
            - Include clear transitions
            - Reference previous concepts
            """
        elif section_type == 'practical':
            prompt += """
            - Apply concepts to real-world scenarios
            - Connect to previous topics
            - Include interactive elements
            - Reinforce key learning points
            """
        elif section_type == 'summary':
            prompt += """
            - Reinforce key takeaways
            - Connect back to objectives
            - Provide next steps
            - End with a strong conclusion
            """
            
        # Add context if available
        if context:
            prompt += f"""
            
            Context:
            - Covered topics: {', '.join(context['covered_topics'])}
            - Pending topics: {', '.join(context['pending_topics'])}
            - Key terms used: {', '.join(context['key_terms'])}
            - Recent narrative: {context['current_narrative']}
            """
            
        # Add requirements
        prompt += f"""
        
        Requirements:
        1. STRICT word count: Generate EXACTLY {target_words} words
        2. Include practical examples: {include_examples}
        3. Use clear transitions
        4. Include engagement points
        5. Use time markers [MM:SS]
        6. Reference specific content from transcript
        7. Maintain narrative flow
        8. Use key terms consistently
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are an expert educator creating a coherent lecture transcript."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=self._calculate_max_tokens(section_type, target_words)
        )
        
        content = response.choices[0].message.content
        word_count = self.text_processor.count_words(content)
        logger.info(f"Section generated: {word_count} words")
        
        return content
        
    def _calculate_max_tokens(self, section_type: str, target_words: int) -> int:
        """Calculate appropriate max_tokens based on section and model"""
        # 1 token ≈ 4 caracteres (1 palabra ≈ 1.33 tokens)
        base_tokens = int(target_words * 1.5)  # Margen para formato
        
        if self.use_thinking_model:
            # Permite hasta 64k tokens pero limita por sección
            section_limits = {
                'introduction': 8000,
                'main': 32000,
                'practical': 16000,
                'summary': 8000
            }
            return min(base_tokens * 2, section_limits.get(section_type, 16000))
        
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
            context['current_topic'] = topic['title']
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