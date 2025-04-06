import os
import gradio as gr
import re
from dotenv import load_dotenv
from src.core.transformer import TranscriptTransformer
from src.utils.pdf_processor import PDFProcessor
from src.utils.text_processor import TextProcessor

load_dotenv()

# Translations dictionary for UI elements
TRANSLATIONS = {
    "en": {
        "title": "AI Script Generator",
        "subtitle": "Transform transcripts and PDFs into timed, structured teaching scripts using AI",
        "input_type_label": "Input Type",
        "input_type_options": ["PDF", "Raw Text"],
        "upload_pdf_label": "Upload Transcript (PDF)",
        "paste_text_label": "Paste Transcript Text",
        "paste_text_placeholder": "Paste your transcript text here...",
        "guiding_prompt_label": "Guiding Prompt (Optional)",
        "guiding_prompt_placeholder": "Additional instructions to customize the output. Examples: 'Use a more informal tone', 'Focus only on section X', 'Generate the content in Spanish', 'Include more practical programming examples', etc.",
        "guiding_prompt_info": "The Guiding Prompt allows you to provide specific instructions to modify the generated content, like output/desired LANGUAGE. You can use it to change the tone, style, focus ONLY on specific sections of the text, specify the output language (e.g., 'Generate in Spanish/French/German'), or give any other instruction that helps personalize the final result.",
        "duration_label": "Target Lecture Duration (minutes)",
        "examples_label": "Include Practical Examples",
        "thinking_model_label": "Use Experimental Thinking Model (Gemini Only)",
        "submit_button": "Transform Transcript",
        "output_label": "Generated Teaching Transcript",
        "error_no_pdf": "Error: No PDF file uploaded",
        "error_no_text": "Error: No text provided",
        "error_prefix": "Error processing transcript: ",
        "language_selector": "Language / Idioma",
        "show_timestamps": "Show Timestamps",
        "hide_timestamps": "Hide Timestamps"
    },
    "es": {
        "title": "Generador de Guiones IA",
        "subtitle": "Transforma transcripciones y PDFs en guiones de enseñanza estructurados y cronometrados usando IA",
        "input_type_label": "Tipo de Entrada",
        "input_type_options": ["PDF", "Texto"],
        "upload_pdf_label": "Subir Transcripción (PDF)",
        "paste_text_label": "Pegar Texto de Transcripción",
        "paste_text_placeholder": "Pega tu texto de transcripción aquí...",
        "guiding_prompt_label": "Instrucciones Guía (Opcional)",
        "guiding_prompt_placeholder": "Instrucciones adicionales para personalizar el resultado. Ejemplos: 'Usa un tono más informal', 'Enfócate solo en la sección X', 'Genera el contenido en inglés', 'Incluye más ejemplos prácticos de programación', etc.",
        "guiding_prompt_info": "Las Instrucciones Guía te permiten proporcionar indicaciones específicas para modificar el contenido generado, como el IDIOMA deseado. Puedes usarlas para cambiar el tono, estilo, enfocarte SOLO en secciones específicas del texto, especificar el idioma de salida (ej., 'Generar en inglés/francés/alemán'), o dar cualquier otra instrucción que ayude a personalizar el resultado final.",
        "duration_label": "Duración Objetivo de la Clase (minutos)",
        "examples_label": "Incluir Ejemplos Prácticos",
        "thinking_model_label": "Usar Modelo de Pensamiento Experimental (Solo Gemini)",
        "submit_button": "Transformar Transcripción",
        "output_label": "Guión de Enseñanza Generado",
        "error_no_pdf": "Error: No se ha subido ningún archivo PDF",
        "error_no_text": "Error: No se ha proporcionado texto",
        "error_prefix": "Error al procesar la transcripción: ",
        "language_selector": "Language / Idioma",
        "show_timestamps": "Mostrar Marcas de Tiempo",
        "hide_timestamps": "Ocultar Marcas de Tiempo"
    }
}

# Language-specific prompt suffixes to append automatically
LANGUAGE_PROMPTS = {
    "en": "",  # Default language doesn't need special instructions
    "es": "Generate the content in Spanish. Genera todo el contenido en español."
}

class TranscriptTransformerApp:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()
        self.current_language = "en"  # Default language
        self.last_generated_content = ""  # Store the last generated content
        self.content_with_timestamps = ""  # Store content with timestamps
        self.content_without_timestamps = ""  # Store content without timestamps
        # Initialize transformer here, assuming Gemini is the primary choice now
        self.transformer = TranscriptTransformer(use_gemini=True) 

    def process_transcript(self, 
                           language: str,
                           input_type: str,
                           file_obj: gr.File = None,
                           raw_text_input: str = "",
                           initial_prompt: str = "",
                           target_duration: int = 30,
                           include_examples: bool = True) -> str:
        """
        Process uploaded transcript and transform it into a teaching transcript
        
        Args:
            language: Selected UI language
            input_type: Type of input (PDF or Raw Text)
            file_obj: Uploaded PDF file (if input_type is PDF)
            raw_text_input: Raw text input (if input_type is Raw Text)
            initial_prompt: Additional guiding instructions for the content generation
            target_duration: Target lecture duration in minutes
            include_examples: Whether to include practical examples
            
        Returns:
            str: Generated teaching transcript
        """
        try:
            # Get text based on input type
            if input_type == TRANSLATIONS[language]["input_type_options"][0]:  # PDF
                if file_obj is None:
                    return TRANSLATIONS[language]["error_no_pdf"]
                raw_text = self.pdf_processor.extract_text(file_obj.name)
            else:  # Raw Text
                if not raw_text_input.strip():
                    return TRANSLATIONS[language]["error_no_text"]
                raw_text = raw_text_input
            
            # Modify initial prompt based on language if no explicit language instruction is given
            modified_prompt = initial_prompt
            
            # Check if user has specified a language in the prompt
            language_keywords = ["spanish", "español", "english", "inglés", "french", "francés", "german", "alemán"]
            user_specified_language = any(keyword in initial_prompt.lower() for keyword in language_keywords)
            
            # Only append language instruction if user hasn't specified one and we have a non-default language
            if not user_specified_language and language in LANGUAGE_PROMPTS and LANGUAGE_PROMPTS[language]:
                if modified_prompt:
                    modified_prompt += " " + LANGUAGE_PROMPTS[language]
                else:
                    modified_prompt = LANGUAGE_PROMPTS[language]
            
            # Transform to teaching transcript with user guidance
            lecture_transcript = self.transformer.transform_to_lecture(
                text=raw_text,
                target_duration=target_duration,
                include_examples=include_examples,
                initial_prompt=modified_prompt
            )
            
            # Store the generated content
            self.content_with_timestamps = lecture_transcript
            
            # Create a version without timestamps
            self.content_without_timestamps = self.remove_timestamps(lecture_transcript)
            
            # Default: show content with timestamps
            self.last_generated_content = lecture_transcript
            
            return lecture_transcript
            
        except Exception as e:
            return f"{TRANSLATIONS[language]['error_prefix']}{str(e)}"
    
    def remove_timestamps(self, text):
        """Remove all timestamps (e.g., [00:00]) from the text"""
        # Regex to match the timestamp pattern [MM:SS] or [HH:MM:SS]
        return re.sub(r'\[\d{1,2}:\d{2}(:\d{2})?\]', '', text)
    
    def toggle_timestamps(self, show_timestamps):
        """Toggle visibility of timestamps in output"""
        if show_timestamps:
            return self.content_with_timestamps
        else:
            return self.content_without_timestamps
    
    def update_ui_language(self, language):
        """Update UI elements based on selected language"""
        self.current_language = language
        
        translations = TRANSLATIONS[language]
        
        return [
            translations["title"],
            translations["subtitle"],
            translations["input_type_label"],
            gr.update(choices=translations["input_type_options"], value=translations["input_type_options"][0]),
            translations["upload_pdf_label"],
            translations["paste_text_label"],
            translations["paste_text_placeholder"],
            translations["guiding_prompt_label"],
            translations["guiding_prompt_placeholder"],
            translations["guiding_prompt_info"],
            translations["duration_label"],
            translations["examples_label"],
            translations["thinking_model_label"],
            translations["submit_button"],
            translations["output_label"]
        ]

    def launch(self):
        """Launch the Gradio interface"""
        # Get the path to the example PDF
        example_pdf = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample2.pdf")
        
        # Map language dropdown values to language codes - Moved here
        lang_map = {
            "🇺🇸 English": "en",
            "🇪🇸 Español": "es"
        }

        with gr.Blocks(title=TRANSLATIONS["en"]["title"]) as interface:
            # Language selector dropdown
            with gr.Row():
                language_selector = gr.Dropdown(
                    choices=list(lang_map.keys()),
                    value="🇺🇸 English",
                    label=TRANSLATIONS["en"]["language_selector"],
                    elem_id="language-selector",
                    interactive=True
                )
            
            # Title
            title_md = gr.Markdown("# " + TRANSLATIONS["en"]["title"])

            # Subtitle
            subtitle_md = gr.Markdown(TRANSLATIONS["en"]["subtitle"])
            
            # Input type row
            with gr.Row():
                input_type = gr.Radio(
                    choices=TRANSLATIONS["en"]["input_type_options"],
                    label=TRANSLATIONS["en"]["input_type_label"],
                    value=TRANSLATIONS["en"]["input_type_options"][1] # Default to Raw Text
                )
            
            # File/text input columns
            with gr.Row():
                # PDF input column starts visible=False as Raw Text is default
                with gr.Column(visible=False) as pdf_column: 
                    file_input = gr.File(
                        label=TRANSLATIONS["en"]["upload_pdf_label"],
                        file_types=[".pdf"]
                    )
                
                # Text input column starts visible=True as Raw Text is default
                with gr.Column(visible=True) as text_column: 
                    text_input = gr.Textbox(
                        label=TRANSLATIONS["en"]["paste_text_label"],
                        lines=10,
                        placeholder=TRANSLATIONS["en"]["paste_text_placeholder"]
                    )
            
            # Guiding prompt 
            with gr.Row():
                initial_prompt = gr.Textbox(
                    label=TRANSLATIONS["en"]["guiding_prompt_label"],
                    lines=3,
                    value="",
                    placeholder=TRANSLATIONS["en"]["guiding_prompt_placeholder"],
                    info=TRANSLATIONS["en"]["guiding_prompt_info"]
                )
            
            # Settings row
            with gr.Row():
                target_duration = gr.Number(
                    label=TRANSLATIONS["en"]["duration_label"],
                    value=30,
                    minimum=2,
                    maximum=60,
                    step=1
                )
                
                include_examples = gr.Checkbox(
                    label=TRANSLATIONS["en"]["examples_label"],
                    value=True
                )
            
            # Submit button
            with gr.Row():
                submit_btn = gr.Button(TRANSLATIONS["en"]["submit_button"])
            
            # Output area
            output = gr.Textbox(
                label=TRANSLATIONS["en"]["output_label"],
                lines=25
            )
            
            # Toggle timestamps button and Copy button
            with gr.Row():
                timestamps_checkbox = gr.Checkbox(
                    label=TRANSLATIONS["en"]["show_timestamps"],
                    value=True,
                    interactive=True
                )
            
            # Handle visibility of input columns based on selection
            def update_input_visibility(language_display, choice):
                language = lang_map.get(language_display, "en") # lang_map is accessible from outer scope
                return [
                    gr.update(visible=(choice == TRANSLATIONS[language]["input_type_options"][0])),  # pdf_column
                    gr.update(visible=(choice == TRANSLATIONS[language]["input_type_options"][1]))  # text_column
                ]
            
            # Get language code from display value
            def get_language_code(language_display):
                return lang_map.get(language_display, "en") # lang_map is accessible from outer scope
            
            # Update UI elements when language changes
            def update_ui_with_display(language_display):
                language = get_language_code(language_display)
                self.current_language = language
                
                translations = TRANSLATIONS[language]
                # Default input type to Raw Text when language changes
                default_input_type = translations["input_type_options"][1] 
                
                return [
                    "# " + translations["title"],  # Title with markdown formatting
                    translations["subtitle"],
                    translations["input_type_label"],
                    # Set default value to Raw Text here as well
                    gr.update(choices=translations["input_type_options"], value=default_input_type, label=translations["input_type_label"]), 
                    gr.update(label=translations["upload_pdf_label"]),
                    gr.update(label=translations["paste_text_label"], placeholder=translations["paste_text_placeholder"]),
                    gr.update(label=translations["guiding_prompt_label"], placeholder=translations["guiding_prompt_placeholder"], info=translations["guiding_prompt_info"]),
                    gr.update(label=translations["duration_label"]),
                    gr.update(label=translations["examples_label"]),
                    # Removed the update for thinking_model_label
                    translations["submit_button"],
                    gr.update(label=translations["output_label"]),
                    gr.update(label=translations["show_timestamps"])
                ]
            
            input_type.change(
                fn=lambda lang_display, choice: update_input_visibility(lang_display, choice),
                inputs=[language_selector, input_type],
                outputs=[pdf_column, text_column]
            )
            
            # Language change event
            language_selector.change(
                fn=update_ui_with_display,
                inputs=language_selector,
                outputs=[
                    title_md, subtitle_md, 
                    input_type, input_type, # input_type repeated as it's updated by this function
                    file_input, text_input,
                    initial_prompt,
                    target_duration, include_examples, # Removed use_thinking_model from outputs
                    submit_btn, output,
                    timestamps_checkbox
                ]
            )
            
            # Toggle timestamps event
            timestamps_checkbox.change(
                fn=self.toggle_timestamps,
                inputs=[timestamps_checkbox],
                outputs=[output]
            )
            
            # Set up submission logic with language code conversion
            submit_btn.click(
                fn=lambda lang_display, *args: self.process_transcript(get_language_code(lang_display), *args),
                inputs=[
                    language_selector,
                    input_type,
                    file_input,
                    text_input,
                    initial_prompt,
                    target_duration,
                    include_examples,
                ],
                outputs=output
            )
            
            # Example for PDF input (assuming example remains PDF for now, adjust if needed)
            # Example data needs one less boolean value now
            gr.Examples(
                examples=[[example_pdf, "", "", 30, True]], 
                # Removed use_thinking_model from inputs list
                inputs=[file_input, text_input, initial_prompt, target_duration, include_examples] 
            )
        
        interface.launch(share=True)

if __name__ == "__main__":
    app = TranscriptTransformerApp()
    app.launch() 