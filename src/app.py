import os
import gradio as gr
from dotenv import load_dotenv
from src.core.transformer import TranscriptTransformer, LocalModelType, APIProvider
from src.utils.pdf_processor import PDFProcessor
from src.utils.text_processor import TextProcessor
from src.utils.tts_processor import TTSProcessor, TTSVoice

# Load environment variables
load_dotenv()

class TranscriptTransformerApp:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()
        self.transformer = None
        self.tts_processor = None

    def process_transcript(self, 
                         file_obj: gr.File, 
                         target_duration: int = 30,
                         include_examples: bool = True,
                         model_type: str = "phi-4",
                         api_provider: str = None,
                         custom_model_name: str = "",
                         openai_key: str = "",
                         gemini_key: str = "",
                         generate_audio: bool = False,
                         voice_model: TTSVoice = "kokoro-82m") -> tuple[str, gr.Audio]:
        """
        Process uploaded transcript and transform it into a teaching transcript
        
        Args:
            file_obj: Uploaded PDF file
            target_duration: Target lecture duration in minutes
            include_examples: Whether to include practical examples
            model_type: Base model type to use
            api_provider: API provider for custom models
            custom_model_name: Custom model name for API providers
            openai_key: OpenAI API key
            gemini_key: Gemini API key
            generate_audio: Whether to generate audio
            voice_model: TTS voice model to use
            
        Returns:
            tuple[str, gr.Audio]: Generated transcript and audio file (if requested)
        """
        try:
            # Set API keys if provided through interface
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
            if gemini_key:
                os.environ["GOOGLE_API_KEY"] = gemini_key
                
            # Determine final model name and provider
            final_model = model_type
            final_provider = None
            
            if api_provider and custom_model_name:
                final_model = custom_model_name
                final_provider = api_provider
            
            # Initialize transformer with selected model
            self.transformer = TranscriptTransformer(
                model_type=final_model,
                api_provider=final_provider
            )
            
            # Extract text from PDF
            raw_text = self.pdf_processor.extract_text(file_obj.name)
            
            # Transform to teaching transcript
            lecture_transcript = self.transformer.transform_to_lecture(
                raw_text,
                target_duration=target_duration,
                include_examples=include_examples
            )
            
            # Generate audio if requested
            audio_file = None
            if generate_audio:
                self.tts_processor = TTSProcessor(voice_model=voice_model)
                audio_path = os.path.join("outputs", "audio", f"lecture_{os.urandom(4).hex()}.wav")
                audio_file = self.tts_processor.generate_audio(lecture_transcript, audio_path)
            
            return lecture_transcript, audio_file
            
        except Exception as e:
            return f"Error processing transcript: {str(e)}", None

    def create_interface(self):
        """Create the Gradio interface"""
        # Get the path to the example PDF
        example_pdf = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample2.pdf")
        
        # Create output directories
        os.makedirs(os.path.join("outputs", "audio"), exist_ok=True)
        
        # Define model choices
        local_models = ["phi-4", "sky-t1-32b", "deepseek-v3"]
        api_providers = ["", "openai", "gemini"]
        default_models = {
            "openai": "gpt-4o-mini",
            "gemini": "gemini-2.0-flash-exp"
        }
        
        # Define duration presets
        duration_presets = ["10 min", "15 min", "30 min", "45 min", "60 min", "Custom"]
        
        with gr.Blocks() as interface:
            gr.Markdown("# Transcript to Teaching Material Transformer")
            gr.Markdown("Transform conversational transcripts into structured teaching material. Uses Microsoft's Phi-4 by default (no API key needed).")
            
            with gr.Row():
                file_input = gr.File(
                    label="Upload Transcript (PDF)",
                    file_types=[".pdf"]
                )
            
            with gr.Row():
                duration_preset = gr.Radio(
                    choices=duration_presets,
                    value="30 min",
                    label="Duration Preset",
                    info="Select a preset duration or choose Custom"
                )
                custom_duration = gr.Number(
                    minimum=5,
                    maximum=120,
                    value=30,
                    label="Custom Duration (minutes)",
                    visible=False,
                    info="Enter duration between 5-120 minutes"
                )
            
            include_examples = gr.Checkbox(
                label="Include Practical Examples",
                value=True
            )
            
            with gr.Row():
                model_type = gr.Radio(
                    choices=local_models,
                    value="phi-4",
                    label="Base Model",
                    info="Local models run without API keys"
                )
                api_provider = gr.Radio(
                    choices=api_providers,
                    value="",
                    label="API Provider",
                    info="Select for using custom models"
                )
            
            custom_model = gr.Textbox(
                label="Custom Model Name",
                placeholder="e.g., gpt-4o-mini or gemini-2.0-flash-exp",
                value="",
                visible=False
            )
            
            custom_context = gr.Number(
                label="Model Context Limit (tokens)",
                info="Set custom context limit for models not in the predefined list",
                visible=False
            )
            
            with gr.Row():
                openai_key = gr.Textbox(
                    label="OpenAI API Key",
                    placeholder="sk-...",
                    type="password",
                    visible=False
                )
                gemini_key = gr.Textbox(
                    label="Gemini API Key",
                    placeholder="YOUR_GEMINI_KEY",
                    type="password",
                    visible=False
                )
            
            with gr.Row():
                generate_audio = gr.Checkbox(
                    label="Generate Audio (Optional)",
                    value=False
                )
                voice_model = gr.Radio(
                    choices=["kokoro-82m"],
                    value="kokoro-82m",
                    label="Voice Model",
                    visible=False
                )
            
            with gr.Row():
                output_text = gr.Textbox(
                    label="Generated Teaching Transcript",
                    lines=25
                )
                output_audio = gr.Audio(
                    label="Generated Audio",
                    visible=False
                )
            
            # Helper function to get duration in minutes
            def get_duration(preset: str, custom: float) -> int:
                if preset == "Custom":
                    return int(custom)
                return int(preset.split()[0])
            
            # Process button
            process_btn = gr.Button("Generate Lecture")
            process_btn.click(
                fn=lambda *args: self.process_transcript(
                    args[0],  # file
                    get_duration(args[1], args[2]),  # duration
                    *args[3:]  # rest of args
                ),
                inputs=[
                    file_input,
                    duration_preset,
                    custom_duration,
                    include_examples,
                    model_type,
                    api_provider,
                    custom_model,
                    openai_key,
                    gemini_key,
                    generate_audio,
                    voice_model
                ],
                outputs=[output_text, output_audio]
            )
            
            # Add interactivity
            def update_custom_duration(preset: str):
                return {"visible": preset == "Custom"}
                
            def update_model_visibility(api_provider: str):
                is_visible = bool(api_provider)
                model_name = default_models.get(api_provider, "")
                return {
                    "visible": is_visible,  # Custom model input
                    "value": model_name
                }, {
                    "visible": is_visible and model_name not in TranscriptTransformer.MODEL_LIMITS  # Context input
                }, {
                    "visible": api_provider == "openai"  # OpenAI key input
                }, {
                    "visible": api_provider == "gemini"  # Gemini key input
                }
                
            def update_voice_visibility(generate_audio: bool):
                return {"visible": generate_audio}
            
            # Update duration field visibility
            duration_preset.change(
                fn=update_custom_duration,
                inputs=[duration_preset],
                outputs=[custom_duration]
            )
            
            # Update model and key fields visibility
            api_provider.change(
                fn=update_model_visibility,
                inputs=[api_provider],
                outputs=[custom_model, custom_context, openai_key, gemini_key]
            )
            
            # Update voice model visibility
            generate_audio.change(
                fn=update_voice_visibility,
                inputs=[generate_audio],
                outputs=[voice_model]
            )
            
            # Add examples
            gr.Examples(
                examples=[
                    [example_pdf, "30 min", 30, True, "phi-4", "", "", "", "", False, "kokoro-82m"]
                ],
                inputs=[
                    file_input,
                    duration_preset,
                    custom_duration,
                    include_examples,
                    model_type,
                    api_provider,
                    custom_model,
                    openai_key,
                    gemini_key,
                    generate_audio,
                    voice_model
                ]
            )
            
        return interface

# Create the Gradio interface
app = TranscriptTransformerApp()
interface = app.create_interface()

# For local development
if __name__ == "__main__":
    interface.launch(share=True)
else:
    # For Hugging Face Spaces deployment
    interface.launch() 