from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import END, MessagesState, START, StateGraph

from .state import (
    DeeperKnowledgeSeekerState,
    ResearcherState,
    SearchQuery,
    ShouldResearchMore,
    PlanResearch,
    DeeperKnowledgeTopics,
    DeeperKnowledgeTopic
)

def plan_research(state: ResearcherState):
    print("🔍 Starting plan_research node")
    print(f"Input state: {state}")
    
    topic = state['topic']
        
    main_instruction = SystemMessage(content=f"""Based on given topic to research make a plan of the research to do. Outcome of research will be used to learn given topic. Topic: {topic}""")
    structured_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(PlanResearch)
    result = structured_llm.invoke([main_instruction])
    print(f"Generated plan: {result.plan}")
    return {"plan": result.plan, "topic": topic} 

def research_router(state: ResearcherState):
    print("🔄 Starting research_router node")
    print(f"Current state: {state}")
    
    # Check if we already have 8 sources
    if isinstance(state, dict):
        current_results = state.get('small_results', [])
    else:
        current_results = state.small_results
        
    if len(current_results) >= 5:
        print("Reached limit of 5 sources. Moving to format results.")
        return 'format_results'
    
    main_instruction = SystemMessage(content=f"""Based on given topic and sources available to it, decide if you need to find more resources to learn this topic. Check if sources covers topic and the plan. Details: {state}""")
    
    structured_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(ShouldResearchMore)
    result = structured_llm.invoke([main_instruction])
    
    next_step = 'search_web' if result.research_more else 'format_results'
    print(f"Decision: Need more research? {result.research_more}. Moving to: {next_step}")
    return next_step
    
def research_search_web(state: ResearcherState):
    print("🌐 Starting research_search_web node")
    
    # Handle state both as dictionary and object
    if isinstance(state, dict):
        topic = state['topic']
        plan = state.get('plan', '')
        current_results = state.get('small_results', [])
    else:
        topic = state.topic
        plan = state.plan
        current_results = state.small_results

    print(f"Topic to research: {topic}")
    print(f"Current plan: {plan}")
    
    main_instruction = SystemMessage(content=f"""Your job is to find resources to learn this topic. Here's the topic: {topic}. Heres the plan: {plan}. Write query that will help fill missing parts of the plan.""")

    # Search
    tavily_search = TavilySearchResults(max_results=2)

    # Search query
    structured_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([main_instruction])
    print(f"Generated search query: {search_query.search_query}")
    
    # Search
    search_docs = tavily_search.invoke(search_query.search_query)
    print(f"Found {len(search_docs)} documents")

    # Add new results to existing ones
    updated_results = current_results + [search_docs]
    
    return {"small_results": updated_results, "topic": topic, "plan": plan}

def format_results(state: ResearcherState):
    print("📝 Starting format_results node")
    print(f"State to format: {state}")
    
    # Handle state both as dictionary and object
    if isinstance(state, dict):
        topic = state['topic']
        results = state.get('small_results', [])
    else:
        topic = state.topic
        results = state.small_results
    
    structured_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(DeeperKnowledgeTopic)
    instruction = f"""Based on results and topic rewrite topic so it has more depth and filled all fields. Topic: {topic}, Results: {results}"""
    result = structured_llm.invoke(instruction)
    print(f"Formatted result: {result}")
    
    return {"deeper_knowledge_results": [result], "topic": topic}

def create_initial_deeper_knowledge_topics(state: DeeperKnowledgeSeekerState):
    print("🎯 Starting create_initial_deeper_knowledge_topics node")
    print(f"Profile: {state.profile}")
    print(f"Topic to research: {state.topic_to_research}")
    
    profile = state.profile
    topic_to_research = state.topic_to_research
    what_is_already_known = state.what_is_already_known
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(DeeperKnowledgeTopics)
    instruction = """
    You are an expert research agent specializing in personalized learning paths. Your task is to analyze the user's profile, expertise level, and current knowledge to identify key topics they should explore to gain a deeper understanding of their area of interest.

    Consider:
    1. The user's professional background and specialization
    2. Their current knowledge level on the topic
    3. What foundational concepts they might be missing
    4. Which advanced topics would be most relevant to their field
    5. Any interdisciplinary connections that could enhance their understanding

    Create a list of at least 10 topics that would be most valuable for this specific user to explore. For each topic:
    - Explain why it's particularly relevant to their profile and specialization
    - Describe how it builds upon or complements their existing knowledge
    - Highlight its practical applications in their field
    
    Do not include topics they already know. Focus on creating a personalized learning path that bridges gaps and extends their expertise in meaningful ways.
    """
    
    system_message = SystemMessage(content=instruction)
    human_message = HumanMessage(content=f"User Profile & Specialization: {profile}\nRequested Topic: {topic_to_research}\nCurrent Knowledge Base: {what_is_already_known}")
    messages = [system_message, human_message]
    response = llm.invoke(messages)
    print(f"Generated {len(response.topics)} initial topics")
    
    return {"topics_ideas": response.topics}

def select_best_topics(state: DeeperKnowledgeSeekerState):
    print("⭐ Starting select_best_topics node")
    print(f"Number of input topics: {len(state.topics_ideas)}")
    
    topics_ideas = state.topics_ideas
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(DeeperKnowledgeTopics)
    instruction = """
    You are an expert research agent specializing in personalized learning paths. Your task is to analyze the provided topics and select the 3 most valuable ones for the user's learning journey.

    Consider:
    1. The user's professional background and current expertise level
    2. How well each topic aligns with their learning goals
    3. The potential impact on their professional development
    4. The logical progression and dependencies between topics
    5. The practical applicability in their field

    Select exactly 3 topics that:
    - Are most critical for building a strong foundation
    - Offer the highest value for their specific profile and goals
    - Create a coherent learning progression
    
    Focus on topics that will have the most significant impact on their understanding and professional growth.
    """
    messages = [SystemMessage(content=instruction), HumanMessage(content=f"Topics: {topics_ideas}, topics will be read by user: {state.profile}. ")]
    response = llm.invoke(messages)
    
    print(f"Selected {len(response.topics)} best topics")
    
    return {"topics_ideas": response.topics}

def initialize_researcher_state(state: DeeperKnowledgeSeekerState):
    print("🔄 Starting initialize_researcher_state node")
    print(f"Initializing research for {len(state.topics_ideas)} topics")
    return [Send("conduct_research", ResearcherState(topic=topic, deeper_knowledge_results=[], small_results=[])) for topic in state.topics_ideas]

def summarize_results(state: DeeperKnowledgeSeekerState):
    print("📊 Starting summarize_results node")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    instruction = f"""
    Write a detailed summary in markdown format based on the research results.
    Include all investigated topics and their findings.
    
    User profile: {state.profile}
    Main topic: {state.topic_to_research}
    Current knowledge: {state.what_is_already_known}
    
    Research results for topics:
    {state.deeper_knowledge_results}
    """
    
    messages = [SystemMessage(content=instruction)]
    response = llm.invoke(messages)
    
    return {"final_result": response.content}