"""
Test the agent system
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.agent_service import run_agent

def test_agent():
    profile = {}
    history = []
    
    test_messages = [
        "Hi, I'm Jane Smith. I'm a software engineer at TechCorp earning $150k. I'm from India on an F-1 OPT and need help with my visa.",
        "What documents do I need?",
        "Can you generate a checklist for me?",
    ]
    
    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"USER: {msg}")
        print('='*60)
        
        result = run_agent(msg, history, profile, case_id=1)
        
        print(f"\nAGENT: {result['response'][:300]}...")
        print(f"\nTools used: {result['tools_used']}")
        print(f"Profile: {result['updated_profile']}")
        
        # Update for next turn
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": result['response']})
        profile = result['updated_profile']

if __name__ == "__main__":
    test_agent()