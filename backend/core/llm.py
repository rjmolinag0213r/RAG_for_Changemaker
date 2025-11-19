
"""LLM integration using llama-cpp-python."""

from typing import Optional, Dict, Any
from llama_cpp import Llama
from backend.config import settings
from backend.utils.logger import log


class LLMModel:
    """Handle LLM operations using Llama 3."""
    
    def __init__(self):
        """Initialize the LLM model."""
        log.info("Initializing LLM Model")
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Llama model."""
        try:
            log.info(f"Loading Llama model from: {settings.llm.model_path}")
            
            self.model = Llama(
                model_path=settings.llm.model_path,
                n_ctx=settings.llm.context_length,
                n_batch=settings.llm.n_batch,
                n_gpu_layers=settings.llm.n_gpu_layers,
                n_threads=settings.llm.n_threads,
                verbose=False
            )
            
            log.info("LLM Model loaded successfully")
            
        except FileNotFoundError:
            log.error(f"Model file not found at: {settings.llm.model_path}")
            log.error("Please download the Llama 3 model and place it in the models directory")
            raise
        except Exception as e:
            log.error(f"Error loading LLM model: {e}")
            raise
    
    def generate(
        self, 
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stop: Optional[list] = None
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            stop: Stop sequences
            
        Returns:
            Generated text
        """
        try:
            if self.model is None:
                raise RuntimeError("Model not loaded")
            
            # Use config defaults if not specified
            if max_tokens is None:
                max_tokens = settings.llm.max_tokens
            if temperature is None:
                temperature = settings.llm.temperature
            if top_p is None:
                top_p = settings.llm.top_p
            
            log.info(f"Generating response (max_tokens={max_tokens}, temp={temperature})")
            
            # Generate response
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                echo=False
            )
            
            # Extract generated text
            generated_text = response['choices'][0]['text'].strip()
            
            log.info(f"Generated {len(generated_text)} characters")
            return generated_text
            
        except Exception as e:
            log.error(f"Error generating text: {e}")
            raise
    
    def generate_chat_response(
        self,
        messages: list,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a chat response using the chat format.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        try:
            # Format messages into a prompt
            prompt = self._format_chat_prompt(messages)
            
            # Generate response
            response = self.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<|eot_id|>", "<|end_of_text|>"]
            )
            
            return response
            
        except Exception as e:
            log.error(f"Error generating chat response: {e}")
            raise
    
    def _format_chat_prompt(self, messages: list) -> str:
        """
        Format messages into Llama 3 chat prompt format.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted prompt
        """
        prompt = "<|begin_of_text|>"
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt += f"<|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == 'user':
                prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == 'assistant':
                prompt += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"
        
        # Add assistant header for response
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
        
        return prompt
