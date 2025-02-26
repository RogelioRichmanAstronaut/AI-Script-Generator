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
                           input_type: str,
                           file_obj: gr.File = None,
                           raw_text_input: str = "",
                           initial_prompt: str = "",
                           target_duration: int = 30,
                           include_examples: bool = True,
                           use_gemini: bool = True,
                           use_thinking_model: bool = False) -> str:
        """
        Process uploaded transcript and transform it into a teaching transcript
        
        Args:
            input_type: Type of input (PDF or Raw Text)
            file_obj: Uploaded PDF file (if input_type is PDF)
            raw_text_input: Raw text input (if input_type is Raw Text)
            initial_prompt: Additional guiding instructions for the content generation
            target_duration: Target lecture duration in minutes
            include_examples: Whether to include practical examples
            use_gemini: Whether to use Gemini API instead of OpenAI
            use_thinking_model: Requires use_gemini=True
            
        Returns:
            str: Generated teaching transcript
        """
        try:
            # Force enable Gemini if thinking model is selected
            if use_thinking_model:
                use_gemini = True
                
            self.transformer = TranscriptTransformer(
                use_gemini=use_gemini,
                use_thinking_model=use_thinking_model
            )
            
            # Get text based on input type
            if input_type == "PDF":
                if file_obj is None:
                    return "Error: No PDF file uploaded"
                raw_text = self.pdf_processor.extract_text(file_obj.name)
            else:  # Raw Text
                if not raw_text_input.strip():
                    return "Error: No text provided"
                raw_text = raw_text_input
            
            # Transform to teaching transcript with user guidance
            lecture_transcript = self.transformer.transform_to_lecture(
                text=raw_text,
                target_duration=target_duration,
                include_examples=include_examples,
                initial_prompt=initial_prompt
            )
            
            return lecture_transcript
            
        except Exception as e:
            return f"Error processing transcript: {str(e)}"

    def launch(self):
        """Launch the Gradio interface"""
        # Get the path to the example PDF
        example_pdf = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample2.pdf")
        
        with gr.Blocks(title="AI Script Generator") as interface:
            gr.Markdown("# AI Script Generator")
            gr.Markdown("Transform transcripts and PDFs into timed, structured teaching scripts using AI")
            
            with gr.Row():
                input_type = gr.Radio(
                    choices=["PDF", "Raw Text"],
                    label="Input Type",
                    value="PDF"
                )
            
            with gr.Row():
                with gr.Column(visible=True) as pdf_column:
                    file_input = gr.File(
                        label="Upload Transcript (PDF)",
                        file_types=[".pdf"]
                    )
                
                with gr.Column(visible=False) as text_column:
                    text_input = gr.Textbox(
                        label="Paste Transcript Text",
                        lines=10,
                        placeholder="Paste your transcript text here..."
                    )
            
            with gr.Row():
                initial_prompt = gr.Textbox(
                    label="Guiding Prompt (Optional)",
                    lines=3,
                    value="",
                    placeholder="Additional instructions to customize the output. Examples: 'Use a more informal tone', 'Focus only on section X', 'Generate the content in Spanish', 'Include more practical programming examples', etc.",
                    info="The Guiding Prompt allows you to provide specific instructions to modify the generated content, like output/desired LANGUAGE. You can use it to change the tone, style, focus ONLY on specific sections of the text, specify the output language (e.g., 'Generate in Spanish/French/German'), or give any other instruction that helps personalize the final result."
                )
            
            with gr.Row():
                target_duration = gr.Number(
                    label="Target Lecture Duration (minutes)",
                    value=30,
                    minimum=2,
                    maximum=60,
                    step=1
                )
                
                include_examples = gr.Checkbox(
                    label="Include Practical Examples",
                    value=True
                )
                
                use_thinking_model = gr.Checkbox(
                    label="Use Experimental Thinking Model (Gemini Only)",
                    value=True
                )
            
            with gr.Row():
                submit_btn = gr.Button("Transform Transcript")
            
            output = gr.Textbox(
                label="Generated Teaching Transcript",
                lines=25
            )
            
            # Handle visibility of input columns based on selection
            def update_input_visibility(choice):
                return [
                    gr.update(visible=(choice == "PDF")),  # pdf_column
                    gr.update(visible=(choice == "Raw Text"))  # text_column
                ]
            
            input_type.change(
                fn=update_input_visibility,
                inputs=input_type,
                outputs=[pdf_column, text_column]
            )
            
            # Set up submission logic
            submit_btn.click(
                fn=self.process_transcript,
                inputs=[
                    input_type,
                    file_input,
                    text_input,
                    initial_prompt,
                    target_duration,
                    include_examples,
                    use_thinking_model
                ],
                outputs=output
            )
            
            # Example for PDF input
            gr.Examples(
                examples=[[example_pdf, "", "", 30, True, True]],
                inputs=[file_input, text_input, initial_prompt, target_duration, include_examples, use_thinking_model]
            )
        
        interface.launch(share=True)

if __name__ == "__main__":
    app = TranscriptTransformerApp()
    app.launch() 