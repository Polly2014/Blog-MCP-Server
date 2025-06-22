"""
Integration tests for AI services
"""

import pytest
import os
from blog_mcp_server.services.ai_service import AIService


class TestAIService:
    """Test cases for AI service integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.ai_service = AIService()
        
    def test_ai_service_initialization(self):
        """Test that AI service initializes correctly"""
        assert self.ai_service is not None
        assert hasattr(self.ai_service, 'providers')
        
    def test_get_available_providers(self):
        """Test that available providers are correctly identified"""
        providers = self.ai_service.get_available_providers()
        assert isinstance(providers, list)
        # Should have at least one provider configured
        assert len(providers) >= 1
        
    @pytest.mark.asyncio
    async def test_generate_content_with_fallback(self):
        """Test content generation with provider fallback"""
        if not os.getenv('DEEPSEEK_API_KEY') and not os.getenv('OPENAI_API_KEY'):
            pytest.skip("No API keys configured for testing")
            
        prompt = "Write a short test message"
        result = await self.ai_service.generate_content(prompt, max_tokens=50)
        assert result is not None
        assert len(result) > 0
        
    def test_cultural_elements_validation(self):
        """Test Naxi cultural elements validation"""
        valid_elements = ["Traditional wooden architecture", "Dongba script"]
        invalid_elements = ["Modern steel construction"]
        
        for element in valid_elements:
            assert self.ai_service.validate_cultural_authenticity(element)
            
        for element in invalid_elements:
            assert not self.ai_service.validate_cultural_authenticity(element)
