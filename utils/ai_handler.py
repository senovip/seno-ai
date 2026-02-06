import google.generativeai as genai
import random
import logging

class GeminiHandler:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.current_key_index = 0
        self._setup_model()

    def _setup_model(self):
        if not self.api_keys:
            logging.error("No API keys provided for Gemini")
            return
        
        # اختيار مفتاح عشوائي أو بالترتيب لضمان التوزيع
        key = self.api_keys[self.current_key_index]
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def get_response(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Error with Gemini API: {e}")
            # محاولة تبديل المفتاح في حال الفشل
            if len(self.api_keys) > 1:
                self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
                self._setup_model()
                return await self.get_response(prompt)
            return "عذراً، واجهت مشكلة في معالجة طلبك حالياً."

    def update_keys(self, new_keys):
        self.api_keys = new_keys
        self.current_key_index = 0
        self._setup_model()
