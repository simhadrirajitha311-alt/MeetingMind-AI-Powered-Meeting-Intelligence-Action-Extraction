from backend.app.ai.llm_provider import DemoLLMProvider


def test_demo_analysis_has_expected_fields():
    provider = DemoLLMProvider()
    analysis = provider.generate_analysis('We decided to launch on Friday. Alice will prepare the deck.')
    assert 'executive_summary' in analysis
    assert 'action_items' in analysis
    assert 'decisions' in analysis
    assert 'sentiment' in analysis
