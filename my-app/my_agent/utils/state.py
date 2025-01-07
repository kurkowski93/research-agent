from typing import List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
import operator
from typing import Annotated

class DeeperKnowledgeTopic(BaseModel):
    topic: str = Field(description="Topic of the knowledge")
    description: str = Field(description="Description of the knowledge")
    why_is_it_important: str = Field(description="Why is it important")
    sources: List[str] = Field(description="Sources of the knowledge", default_factory=list)
    
# main flow schemas
        
class DeeperKnowledgeSeekerState(BaseModel):
    profile: str = Field(description="Profile of the person who is asking for deeper knowledge")
    topic_to_research: str = Field(description="Topic of the knowledge to research")    
    what_is_already_known: str = Field(description="What is already known about the topic")
    topics_ideas: List[DeeperKnowledgeTopic] = Field(default_factory=list, description="List of topics and ideas")
    deeper_knowledge_results: Annotated[List[DeeperKnowledgeTopic], operator.add] = Field(default_factory=list, description="List Deeper knowledge topics to find")
    results: Annotated[List[str], operator.add] = Field(default_factory=list, description="Results of the research")
    final_result: str = Field(default="", description="Final result of the research")
    
class DeeperKnowledgeTopics(BaseModel):
    topics: List[DeeperKnowledgeTopic] = Field(description="List of deeper knowledge topics")
    
# subgraphs schemas    
class ResearcherState(MessagesState):
    topic: DeeperKnowledgeTopic = Field(description="Topic of the knowledge to research")
    deeper_knowledge_results: List[DeeperKnowledgeTopic] = Field(default_factory=list, description="List of deeper knowledge topics")
    small_results: Annotated[List[str], operator.add] = Field(default_factory=list, description="Results of the search")
    query_to_ask: str = Field(default="", description="Query to ask")
    plan: str = Field(default="", description="Plan of the research")

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")
    stop: bool = Field(None, description="Stop search")
    
class ShouldResearchMore(BaseModel):
    research_more: bool = Field(None, description="Should research more")
    
class PlanResearch(BaseModel):
    plan: str = Field(None, description="Plan of the research") 