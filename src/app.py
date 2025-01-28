import os
import gradio as gr
from dotenv import load_dotenv
from src.core.transformer import TranscriptTransformer
from src.utils.pdf_processor import PDFProcessor
from src.utils.text_processor import TextProcessor

load_dotenv()

class TranscriptTransformerApp:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()

    def process_transcript(self, 
                         file_obj: gr.File, 
                         target_duration: int = 30,
                         include_examples: bool = True,
                         use_gemini: bool = True) -> str:
        """
        Process uploaded transcript and transform it into a teaching transcript
        
        Args:
            file_obj: Uploaded PDF file
            target_duration: Target lecture duration in minutes
            include_examples: Whether to include practical examples
            use_gemini: Whether to use Gemini API instead of OpenAI
            
        Returns:
            str: Generated teaching transcript
        """
        try:
            # Initialize transformer with selected model
            self.transformer = TranscriptTransformer(use_gemini=use_gemini)
            
            # Extract text from PDF
            raw_text = self.pdf_processor.extract_text(file_obj.name)
            
            # Transform to teaching transcript
            lecture_transcript = self.transformer.transform_to_lecture(
                raw_text,
                target_duration=target_duration,
                include_examples=include_examples
            )
            
            return lecture_transcript
            
        except Exception as e:
            return f"Error processing transcript: {str(e)}"

    def launch(self):
        """Launch the Gradio interface"""
        # Get the path to the example PDF
        example_pdf = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample2.pdf")
        
        interface = gr.Interface(
            fn=self.process_transcript,
            inputs=[
                gr.File(
                    label="Upload Transcript (PDF)",
                    file_types=[".pdf"]
                ),
                gr.Slider(
                    minimum=30,
                    maximum=60,
                    value=30,
                    step=15,
                    label="Target Lecture Duration (minutes)"
                ),
                gr.Checkbox(
                    label="Include Practical Examples",
                    value=True
                ),
                gr.Checkbox(
                    label="Use Gemini API (instead of OpenAI)",
                    value=True
                )
            ],
            outputs=gr.Textbox(
                label="Generated Teaching Transcript",
                lines=25
            ),
            title="Transcript to Teaching Material Transformer",
            description="Transform conversational transcripts into structured teaching material",
            examples=[
                [example_pdf, 30, True, True]
            ],
            cache_examples=True
        )
        
        interface.launch(share=True)

if __name__ == "__main__":
    app = TranscriptTransformerApp()
    app.launch() 