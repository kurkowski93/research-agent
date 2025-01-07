from typing import Dict, List, Tuple, TypedDict, Literal
from langgraph.graph import END, StateGraph, START

from my_agent.utils.nodes import (
    plan_research,
    research_router,
    research_search_web,
    format_results,
    create_initial_deeper_knowledge_topics,
    select_best_topics,
    initialize_researcher_state,
    summarize_results
)
from my_agent.utils.state import DeeperKnowledgeSeekerState, ResearcherState



# Create research subgraph
def create_research_graph() -> StateGraph:
    research_workflow = StateGraph(ResearcherState)
    
    # Add nodes
    research_workflow.add_node("plan_research", plan_research)
    research_workflow.add_node("search_web", research_search_web)
    research_workflow.add_node("format_results", format_results)
    
    # Add edges
    research_workflow.add_edge(START, "plan_research")
    research_workflow.add_edge("plan_research", "search_web")
    research_workflow.add_conditional_edges(
        "search_web",
        research_router,
        {
            "search_web": "search_web",
            "format_results": "format_results"
        }
    )
    research_workflow.add_edge("format_results", END)
    
    return research_workflow.compile()

main_graph_builder = StateGraph(DeeperKnowledgeSeekerState)
main_graph_builder.add_node("create_initial_deeper_knowledge_topics", create_initial_deeper_knowledge_topics)
main_graph_builder.add_node("select_best_topics", select_best_topics)
main_graph_builder.add_node("conduct_research", create_research_graph())
main_graph_builder.add_node("summarize_results", summarize_results)

main_graph_builder.add_edge(START, "create_initial_deeper_knowledge_topics")
main_graph_builder.add_edge("create_initial_deeper_knowledge_topics", "select_best_topics")
main_graph_builder.add_conditional_edges("select_best_topics", initialize_researcher_state, ['conduct_research'])
main_graph_builder.add_edge("conduct_research", "summarize_results")
main_graph_builder.add_edge("summarize_results", END)

# Compile graph
graph = main_graph_builder.compile() 