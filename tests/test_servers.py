"""
Test suite for Blog MCP Server
"""

import pytest
import asyncio
from blog_mcp_server.content_server import app as content_app
from blog_mcp_server.guesthouse_server import app as guesthouse_app
from blog_mcp_server.media_server import app as media_app
from blog_mcp_server.management_server import app as management_app


class TestContentServer:
    """Test cases for content generation server"""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test that content server initializes correctly"""
        assert content_app is not None
        
    @pytest.mark.asyncio
    async def test_generate_blog_post_tool_exists(self):
        """Test that generate_blog_post tool is available"""
        tools = content_app.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "generate_blog_post" in tool_names


class TestGuesthouseServer:
    """Test cases for guesthouse management server"""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test that guesthouse server initializes correctly"""
        assert guesthouse_app is not None
        
    @pytest.mark.asyncio
    async def test_design_guesthouse_tool_exists(self):
        """Test that design_guesthouse tool is available"""
        tools = guesthouse_app.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "design_guesthouse" in tool_names


class TestMediaServer:
    """Test cases for media generation server"""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test that media server initializes correctly"""
        assert media_app is not None
        
    @pytest.mark.asyncio
    async def test_generate_image_tool_exists(self):
        """Test that generate_image tool is available"""
        tools = media_app.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "generate_image" in tool_names


class TestManagementServer:
    """Test cases for blog management server"""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test that management server initializes correctly"""
        assert management_app is not None
        
    @pytest.mark.asyncio
    async def test_analyze_blog_performance_tool_exists(self):
        """Test that analyze_blog_performance tool is available"""
        tools = management_app.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "analyze_blog_performance" in tool_names


if __name__ == "__main__":
    pytest.main([__file__])
