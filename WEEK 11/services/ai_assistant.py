from typing import List, Dict
import streamlit as st


class AIAssistant:
    """Simple wrapper around an AI/chat model.
    In your real project, connect this to OpenAI or another provider.
    """
    
    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        self._system_prompt = system_prompt
        self._history: List[Dict[str, str]] = []
        self._client = None
        self._enabled = False
        
        # Try to initialize OpenAI client
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            self._enabled = True
        except Exception:
            # If OpenAI is not available, fall back to fake responses
            self._client = None
            self._enabled = False
    
    def set_system_prompt(self, prompt: str) -> None:
        """Update the system prompt for the AI assistant."""
        self._system_prompt = prompt
    
    def send_message(self, user_message: str) -> str:
        """Send a message and get a response.
        Replace this body with your real API call.
        """
        self._history.append({"role": "user", "content": user_message})
        
        if self._enabled and self._client:
            try:
                # Real OpenAI API call
                messages = [{"role": "system", "content": self._system_prompt}]
                messages.extend(self._history)
                
                response = self._client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
                self._history.append({"role": "assistant", "content": ai_response})
                return ai_response
                
            except Exception as e:
                # If API call fails, use fallback
                response = f"[AI error - using fallback]: {user_message[:50]}"
                self._history.append({"role": "assistant", "content": response})
                return response
        else:
            # Fake response for when OpenAI is not available
            response = f"[AI reply to]: {user_message[:50]}"
            self._history.append({"role": "assistant", "content": response})
            return response
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self._history.clear()
