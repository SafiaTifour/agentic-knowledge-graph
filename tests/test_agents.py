import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_entity_extractor():
    from src.schemas.agent_schemas import EntityExtractorResponse
    from src.agents.entity_extractor import extract_entities
    
    with patch("src.agents.entity_extractor.structured_llm.ainvoke") as mock_ainvoke:
        mock_response = EntityExtractorResponse(entities=["Alan Turing", "Computer Science"])
        # Mock the async return value
        mock_ainvoke.return_value = mock_response
        
        result = await extract_entities("Who was Alan Turing in Computer Science?")
        assert result == ["Alan Turing", "Computer Science"]
        mock_ainvoke.assert_called_once()
