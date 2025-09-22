import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import sys
import os

# Add the parent directory to the path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.openai_services import OpenAIService


class TestChatMemory:
    """Test suite for verifying conversation memory functionality in OpenAI service."""
    
    @pytest.fixture
    def openai_service(self):
        """Create OpenAI service instance with mock API key."""
        return OpenAIService(api_key="test-api-key")
    
    def test_build_conversation_with_empty_history(self, openai_service):
        """Test that conversation is built correctly with empty history."""
        system_prompt = "You are a helpful assistant"
        history = []
        current_message = "Hello, I need help with booking"
        
        result = openai_service._build_conversation(system_prompt, history, current_message)
        
        assert len(result) == 2
        assert result[0] == {"role": "system", "content": system_prompt}
        assert result[1] == {"role": "user", "content": current_message}
    
    def test_build_conversation_with_short_history(self, openai_service):
        """Test conversation building with short history (under 10 messages)."""
        system_prompt = "You are a helpful assistant"
        history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
            {"role": "user", "content": "Second message"},
            {"role": "assistant", "content": "Second response"}
        ]
        current_message = "Current message"
        
        result = openai_service._build_conversation(system_prompt, history, current_message)
        
        assert len(result) == 6  # system + 4 history + current
        assert result[0] == {"role": "system", "content": system_prompt}
        assert result[1:5] == history
        assert result[5] == {"role": "user", "content": current_message}
    
    def test_build_conversation_truncates_long_history(self, openai_service):
        """Test that conversation history is truncated to last 10 messages."""
        system_prompt = "You are a helpful assistant"
        # Create 15 messages in history
        history = []
        for i in range(15):
            history.append({"role": "user", "content": f"Message {i}"})
            history.append({"role": "assistant", "content": f"Response {i}"})
        
        current_message = "Current message"
        
        result = openai_service._build_conversation(system_prompt, history, current_message)
        
        # Should have system + last 10 from history + current = 12 total
        assert len(result) == 12
        assert result[0] == {"role": "system", "content": system_prompt}
        assert result[1:11] == history[-10:]  # Last 10 messages
        assert result[11] == {"role": "user", "content": current_message}
    
    def test_build_conversation_preserves_message_order(self, openai_service):
        """Test that message order is preserved in conversation building."""
        system_prompt = "You are a helpful assistant"
        history = [
            {"role": "user", "content": "First user message"},
            {"role": "assistant", "content": "First assistant response"},
            {"role": "user", "content": "Second user message"},
            {"role": "assistant", "content": "Second assistant response"}
        ]
        current_message = "Latest user message"
        
        result = openai_service._build_conversation(system_prompt, history, current_message)
        
        expected = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "First user message"},
            {"role": "assistant", "content": "First assistant response"},
            {"role": "user", "content": "Second user message"},
            {"role": "assistant", "content": "Second assistant response"},
            {"role": "user", "content": current_message}
        ]
        
        assert result == expected
    
    def test_build_conversation_handles_none_history_gracefully(self, openai_service):
        """Test that None history is handled gracefully after fix."""
        system_prompt = "You are a helpful assistant"
        current_message = "Hello"
        
        # After fix, should handle None gracefully
        result = openai_service._build_conversation(system_prompt, None, current_message)
        
        assert len(result) == 2
        assert result[0] == {"role": "system", "content": system_prompt}
        assert result[1] == {"role": "user", "content": current_message}
    
    @pytest.mark.asyncio
    async def test_get_frustration_response_uses_conversation_history(self, openai_service):
        """Test that get_frustration_response properly uses conversation history."""
        conversation_history = [
            {"role": "user", "content": "I want to book a room"},
            {"role": "assistant", "content": "What dates are you looking for?"},
            {"role": "user", "content": "Next weekend"}
        ]
        user_message = "Do you have availability?"
        
        # Create properly structured mock response
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "Let me check that for you..."
        
        # Fix the async iterator mock
        async def mock_async_iter():
            yield mock_chunk
        
        mock_response = MagicMock()
        mock_response.__aiter__ = mock_async_iter
        
        # Mock the create method
        mock_create = AsyncMock(return_value=mock_response)
        
        with patch.object(openai_service.client.chat.completions, 'create', mock_create):
            response_generator = openai_service.get_frustration_response(
                user_message, conversation_history, frustration_level=1
            )
            
            # Collect responses
            responses = []
            async for response in response_generator:
                responses.append(response)
                if response.get("type") == "message_chunk":
                    break
        
        # Verify that the client was called
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]  # Get keyword arguments
        messages = call_args['messages']
        
        # Verify conversation structure (accounting for implementation details)
        assert len(messages) >= len(conversation_history) + 2  # system + history + current (+ possibly helpful prompt)
        assert messages[0]['role'] == 'system'
        
        # Verify history is included correctly
        found_user_messages = [msg for msg in messages if msg.get('role') == 'user']
        
        # Should contain at least the history messages and current message
        history_user_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
        for hist_content in history_user_messages:
            assert any(hist_content in msg['content'] for msg in found_user_messages), f"History message '{hist_content}' not found"
    
    @pytest.mark.asyncio
    async def test_memory_context_influences_responses(self, openai_service):
        """Test that conversation history context is properly sent to the AI model."""
        history = [
            {"role": "user", "content": "My name is John"},
            {"role": "assistant", "content": "Nice to meet you, John!"},
            {"role": "user", "content": "I prefer luxury hotels"},
            {"role": "assistant", "content": "I'll keep your preference for luxury accommodations in mind."}
        ]
        current_message = "What do you recommend?"
        
        # Create mock response
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "Based on your preferences..."
        
        async def mock_async_iter():
            yield mock_chunk
        
        mock_response = MagicMock()
        mock_response.__aiter__ = mock_async_iter
        mock_create = AsyncMock(return_value=mock_response)
        
        with patch.object(openai_service.client.chat.completions, 'create', mock_create):
            response_generator = openai_service.get_frustration_response(
                current_message, history, frustration_level=1
            )
            
            # Consume the generator
            async for response in response_generator:
                if response.get("type") == "message_chunk":
                    break
        
        # Verify the complete conversation context was sent
        call_args = mock_create.call_args[1]
        messages = call_args['messages']
        
        # Convert messages to string for easier searching
        messages_str = str(messages)
        
        # Check that historical context is present
        assert "John" in messages_str, "User's name from history should be in context"
        assert "luxury" in messages_str.lower(), "User preferences should be in context"
    
    def test_memory_overflow_preserves_recent_context(self, openai_service):
        """Test that when history exceeds 10 messages, the most recent ones are preserved."""
        system_prompt = "You are a helpful assistant"
        
        # Create 15 messages with identifiable content
        history = []
        for i in range(15):
            history.append({"role": "user", "content": f"User message {i}"})
        
        current_message = "Final message"
        
        result = openai_service._build_conversation(system_prompt, history, current_message)
        
        # Should preserve last 10 messages (indices 5-14)
        preserved_user_messages = [msg['content'] for msg in result if msg["role"] == "user"][:-1]  # Exclude current message
        
        assert len(preserved_user_messages) == 10, f"Expected 10 preserved messages, got {len(preserved_user_messages)}"
        
        # Verify that the most recent messages are preserved (messages 5-14)
        expected_messages = [f"User message {i}" for i in range(5, 15)]
        assert preserved_user_messages == expected_messages
    
    @pytest.mark.asyncio 
    async def test_conversation_continuity_across_multiple_turns(self, openai_service):
        """Test that memory is maintained across multiple conversation turns."""
        conversation_turns = [
            ("Hi, I'm looking for a hotel", []),
            ("I need it for next weekend", [
                {"role": "user", "content": "Hi, I'm looking for a hotel"},
                {"role": "assistant", "content": "I'd be happy to help you find a hotel!"}
            ]),
            ("What about pricing?", [
                {"role": "user", "content": "Hi, I'm looking for a hotel"},
                {"role": "assistant", "content": "I'd be happy to help you find a hotel!"},
                {"role": "user", "content": "I need it for next weekend"},
                {"role": "assistant", "content": "Great! Let me check availability for next weekend."}
            ])
        ]
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "Response chunk"
        
        async def mock_async_iter():
            yield mock_chunk
        
        mock_response = MagicMock()
        mock_response.__aiter__ = mock_async_iter
        mock_create = AsyncMock(return_value=mock_response)
        
        with patch.object(openai_service.client.chat.completions, 'create', mock_create):
            for i, (message, history) in enumerate(conversation_turns):
                response_generator = openai_service.get_frustration_response(
                    message, history, frustration_level=1
                )
                
                async for response in response_generator:
                    if response.get("type") == "message_chunk":
                        break
                
                # Verify that history is properly included in the conversation
                call_args = mock_create.call_args[1]
                messages = call_args['messages']
                
                # Verify minimum expected messages and that history is included
                minimum_expected = 1 + len(history) + 1  # system + history + current
                assert len(messages) >= minimum_expected, f"Turn {i}: Expected at least {minimum_expected} messages, got {len(messages)}"
                
                # Verify that all history messages are present in the conversation
                if history:
                    for hist_msg in history:
                        found = any(
                            msg.get("role") == hist_msg["role"] and hist_msg["content"] in msg.get("content", "")
                            for msg in messages
                        )
                        assert found, f"Turn {i}: History message {hist_msg} not found in conversation"
    
    def test_memory_with_exactly_10_messages(self, openai_service):
        """Test edge case with exactly 10 messages in history."""
        system_prompt = "You are a helpful assistant"
        history = [{"role": "user", "content": f"Message {i}"} for i in range(10)]
        current_message = "Current message"
        
        result = openai_service._build_conversation(system_prompt, history, current_message)
        
        assert len(result) == 12  # system + 10 history + current
        assert result[0] == {"role": "system", "content": system_prompt}
        assert result[1:11] == history
        assert result[11] == {"role": "user", "content": current_message}
    
    def test_conversation_memory_persistence_across_calls(self, openai_service):
        """Test that conversation can be built consistently across multiple calls."""
        # First conversation turn
        history1 = []
        message1 = "Hello"
        
        conversation1 = openai_service._build_conversation(
            "System prompt", history1, message1
        )
        
        # Second conversation turn - add previous exchange to history
        history2 = [
            {"role": "user", "content": message1},
            {"role": "assistant", "content": "Hello! How can I help you?"}
        ]
        message2 = "I need help with booking"
        
        conversation2 = openai_service._build_conversation(
            "System prompt", history2, message2
        )
        
        # Verify that second conversation includes previous context
        assert len(conversation2) == 4  # system + 2 history + current
        assert conversation2[1] == {"role": "user", "content": message1}
        assert conversation2[2] == {"role": "assistant", "content": "Hello! How can I help you?"}
        assert conversation2[3] == {"role": "user", "content": message2}
    
    def test_build_conversation_with_mixed_message_types(self, openai_service):
        """Test conversation building with different message types in history."""
        system_prompt = "You are a helpful assistant"
        history = [
            {"role": "user", "content": "Book a room"},
            {"role": "assistant", "content": "What type of room?"},
            {"role": "user", "content": "Single room"},
            {"role": "assistant", "content": "Let me check availability"}
        ]
        current_message = "Any updates?"
        
        result = openai_service._build_conversation(system_prompt, history, current_message)
        
        # Verify all roles are preserved
        roles = [msg["role"] for msg in result]
        expected_roles = ["system", "user", "assistant", "user", "assistant", "user"]
        assert roles == expected_roles


# Additional tests for edge cases and error handling
class TestChatMemoryEdgeCases:
    """Additional tests for edge cases and error scenarios."""
    
    @pytest.fixture
    def openai_service(self):
        return OpenAIService(api_key="test-api-key")
    
    def test_empty_message_handling(self, openai_service):
        """Test handling of empty messages."""
        system_prompt = "System"
        history = [{"role": "user", "content": "Previous message"}]
        current_message = ""
        
        result = openai_service._build_conversation(system_prompt, history, current_message)
        
        assert len(result) == 3
        assert result[-1]["content"] == ""
    
    def test_malformed_history_messages(self, openai_service):
        """Test handling of malformed history messages."""
        system_prompt = "System"
        # History with missing 'content' key
        history = [{"role": "user"}]  # Missing content
        current_message = "Test"
        
        # This should probably be handled more gracefully in the implementation
        result = openai_service._build_conversation(system_prompt, history, current_message)
        assert len(result) == 3
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, openai_service):
        """Test that API errors are properly handled."""
        history = [{"role": "user", "content": "Test"}]
        current_message = "Test message"
        
        # Mock an API error in the stream method
        mock_create = AsyncMock(side_effect=Exception("API Error"))
        
        # Also need to mock random.choice to ensure we get the direct path
        with patch.object(openai_service.client.chat.completions, 'create', mock_create), \
             patch('random.choice', return_value=True):  # Force immediate frustrating response
            response_generator = openai_service.get_frustration_response(
                current_message, history, frustration_level=1
            )
            
            responses = []
            async for response in response_generator:
                responses.append(response)
                break  # Get the error response
            
            # Should return an error response as message_chunk
            assert len(responses) > 0
            # The implementation returns error messages as message_chunk with Italian text
            assert responses[0]["type"] == "message_chunk"
            assert "problema tecnico" in responses[0]["data"]