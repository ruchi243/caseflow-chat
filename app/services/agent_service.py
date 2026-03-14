"""
Agent Orchestrator
Reads conversation, decides which tools to call, returns response.
"""
from app.services.llm_service import ollama_service
from app.services import agent_tools
from typing import List, Dict, Optional
import json


SYSTEM_PROMPT = """You are Caseflow, an expert immigration case intake assistant for a law firm.

Your job is to:
1. Gather information about the applicant's immigration needs
2. Identify the appropriate visa type
3. Generate document checklists
4. Answer questions using the knowledge base
5. Draft letters when requested

You have access to these tools. Decide which to call based on the conversation:
- extract_profile: when user shares personal/employment info
- identify_visa_type: when you have enough info to determine visa type
- retrieve_knowledge: when you need to answer immigration questions
- generate_checklist: when visa type is known and user wants documents list
- draft_letter: when user requests a letter
- summarize_case: when asked for a case summary

Always be professional, empathetic, and thorough.
Ask follow-up questions to gather missing information.
Always cite your sources when referencing immigration rules."""


def decide_tools(message: str, conversation_history: List[Dict], profile: Dict) -> List[str]:
    """
    Ask the LLM which tools to use for this message.
    Returns list of tool names to call.
    """
    prompt = f"""Given this user message and conversation context, which tools should be called?

User message: {message}

Known profile so far: {json.dumps(profile)}

Available tools:
- extract_profile: user shared personal/job/education info
- identify_visa_type: enough info to determine visa type  
- retrieve_knowledge: user asked an immigration question
- generate_checklist: user wants document list
- draft_letter: user wants a letter written
- summarize_case: user wants case summary
- none: just respond conversationally

Rules:
- Only include extract_profile if the message contains actual personal/job info
- Only include identify_visa_type if you have enough info to make a determination
- Return ["none"] for simple follow-up questions that just need a conversational reply
- Never include identify_visa_type if profile already contains visa_type

Return ONLY a JSON array. No explanation. Just the array."""

    response = ollama_service.generate(prompt)
    
    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        tools = json.loads(clean)
        return tools if isinstance(tools, list) else ["none"]
    except:
        return ["retrieve_knowledge"]  # Default to knowledge search


def run_agent(
    message: str,
    conversation_history: List[Dict],
    profile: Dict,
    case_id: int
) -> Dict:
    """
    Main agent function. 
    1. Decides which tools to call
    2. Runs the tools
    3. Generates a response
    
    Returns dict with response, tool results, citations, updated profile.
    """
    tool_results = []
    citations = []
    updated_profile = profile.copy()
    audit_log = []

    # Step 1: Decide which tools to call
    tools_to_call = decide_tools(message, conversation_history, profile)
    audit_log.append({"action": "decided_tools", "tools": tools_to_call})
    

    # Step 2: Run each tool
    for tool_name in tools_to_call:
        if tool_name == "none":
            continue

        try:
            if tool_name == "extract_profile":
                result = agent_tools.extract_profile(message)
                # Merge into profile (don't overwrite with null)
                for k, v in result.items():
                    if v and v != "null" and k != "parse_error" and k != "raw_extraction":
                        updated_profile[k] = v
                tool_results.append({"tool": "extract_profile", "result": result})
                audit_log.append({"action": "extracted_profile", "result": result})

            elif tool_name == "identify_visa_type":
                # Don't re-identify if already set
                if updated_profile.get("visa_type"):
                    audit_log.append({"action": "skipped_identify_visa", "reason": "already set"})
                    continue
                result = agent_tools.identify_visa_type(updated_profile, message)
                if result.get("visa_type"):
                    updated_profile["visa_type"] = result["visa_type"]
                tool_results.append({"tool": "identify_visa_type", "result": result})
                audit_log.append({"action": "identified_visa", "result": result})

            elif tool_name == "retrieve_knowledge":
                result = agent_tools.retrieve_knowledge(message)
                tool_results.append({"tool": "retrieve_knowledge", "result": result})
                # Collect citations
                for r in result:
                    citations.append(r.get("citation", {}))
                audit_log.append({"action": "retrieved_knowledge", "chunks": len(result)})

            elif tool_name == "generate_checklist":
                visa_type = updated_profile.get("visa_type", "H-1B")
                result = agent_tools.generate_checklist(visa_type, updated_profile)
                tool_results.append({"tool": "generate_checklist", "result": result})
                audit_log.append({"action": "generated_checklist", "visa_type": visa_type})

            elif tool_name == "draft_letter":
                result = agent_tools.draft_letter(
                    "cover letter",
                    updated_profile,
                    message
                )
                tool_results.append({"tool": "draft_letter", "result": result})
                audit_log.append({"action": "drafted_letter"})

            elif tool_name == "summarize_case":
                result = agent_tools.summarize_case(conversation_history, updated_profile)
                tool_results.append({"tool": "summarize_case", "result": result})
                audit_log.append({"action": "summarized_case"})

        except Exception as e:
            audit_log.append({"action": f"tool_error_{tool_name}", "error": str(e)})

    # Step 3: Build context for final response
    tool_context = ""
    for tr in tool_results:
        tool_name = tr["tool"]
        result = tr["result"]
        if tool_name == "retrieve_knowledge":
            for r in result:
                tool_context += f"\nKnowledge: {r['text']}\nSource: {r['citation_formatted']}\n"
        elif tool_name == "generate_checklist":
            tool_context += f"\nChecklist generated: {json.dumps(result)}\n"
        elif tool_name == "extract_profile":
            tool_context += f"\nExtracted profile info: {json.dumps(result)}\n"
        elif tool_name == "identify_visa_type":
            tool_context += f"\nVisa recommendation: {json.dumps(result)}\n"
        elif tool_name in ["draft_letter", "summarize_case"]:
            tool_context += f"\n{result}\n"

    # Step 4: Generate final response
    messages = conversation_history + [{"role": "user", "content": message}]
    
    final_prompt = f"""{SYSTEM_PROMPT}
    

Tool results from this turn:
{tool_context if tool_context else "No tools called - respond conversationally."}

Conversation so far:
{chr(10).join([f"{m['role'].upper()}: {m['content']}" for m in messages[-6:]])}

Respond as Caseflow. Be helpful and professional.
- Never dump raw JSON in your response
- Present checklists as readable bullet points
- If you used knowledge base results, mention the source naturally
- Keep responses concise and focused"""
    response_text = ollama_service.generate(final_prompt)

    return {
        "response": response_text,
        "tool_results": tool_results,
        "citations": citations,
        "updated_profile": updated_profile,
        "audit_log": audit_log,
        "tools_used": [t for t in tools_to_call if t != "none"]
    }