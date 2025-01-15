import os
import torch
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Literal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TTSVoice = Literal["kokoro-82m"]

class TTSProcessor:
    """Text-to-Speech processor using Hugging Face models"""
    
    KOKORO_MODEL_ID = "hexgrad/Kokoro-82M"
    
    def __init__(self, voice_model: TTSVoice = "kokoro-82m"):
        """Initialize TTS processor with selected voice model"""
        self.voice_model = voice_model
        
        if voice_model == "kokoro-82m":
            logger.info("Initializing Kokoro-82M TTS model")
            self.tokenizer = AutoTokenizer.from_pretrained(self.KOKORO_MODEL_ID)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.KOKORO_MODEL_ID,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.model.eval()
    
    def generate_audio(self, text: str, output_path: str) -> str:
        """
        Generate audio from text and save to file
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            
        Returns:
            str: Path to generated audio file
        """
        try:
            logger.info("Generating audio from text")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Generate audio based on model
            if self.voice_model == "kokoro-82m":
                inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
                
                with torch.no_grad():
                    audio_values = self.model.generate(
                        **inputs,
                        do_sample=True,
                        temperature=0.7,
                        max_new_tokens=1000
                    )
                
                # Save audio
                audio_values = audio_values.cpu().numpy().squeeze()
                torch.save(audio_values, output_path)
                
                logger.info(f"Audio saved to {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise 