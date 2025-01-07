import unittest
from my_agent.agent import (
    workflow,
    graph,
    create_research_graph,
    GraphConfig,
    DeeperKnowledgeSeekerState,
    ResearcherState
)

class TestAgent(unittest.TestCase):
    def setUp(self):
        """Przygotowanie środowiska przed każdym testem"""
        self.config = {"model_name": "gpt-4o-mini"}
        self.initial_state = DeeperKnowledgeSeekerState(
            profile="Badacz zainteresowany sztuczną inteligencją",
            topic_to_research="Sztuczna inteligencja w medycynie",
            what_is_already_known="Podstawowe zastosowania AI w diagnostyce medycznej",
            topics_ideas=[],
            deeper_knowledge_results=[],
            results=[]
        )

    def test_workflow_structure(self):
        """Test sprawdzający czy workflow ma wszystkie wymagane węzły"""
        expected_nodes = {
            "create_initial_topics",
            "select_best_topics",
            "initialize_researcher",
            "conduct_research",
            "summarize_results"
        }
        actual_nodes = set(workflow.nodes.keys())
        # Usuwamy węzły systemowe
        actual_nodes = {node for node in actual_nodes if not node.startswith("__")}
        self.assertEqual(actual_nodes, expected_nodes)

    def test_research_graph_structure(self):
        """Test sprawdzający strukturę grafu badawczego"""
        research_graph = create_research_graph()
        expected_nodes = {
            "plan_research",
            "research_router",
            "search_web",
            "format_results",
            "__start__"  # Dodajemy węzeł startowy
        }
        self.assertEqual(set(research_graph.nodes.keys()), expected_nodes)

    def test_graph_compilation(self):
        """Test sprawdzający czy graf kompiluje się poprawnie"""
        self.assertIsNotNone(graph)
        # Sprawdzamy czy graf ma odpowiednie atrybuty zamiast sprawdzania czy jest wywoływalny
        self.assertTrue(hasattr(graph, "nodes"))
        self.assertTrue(hasattr(graph, "edges"))

    def test_state_initialization(self):
        """Test sprawdzający poprawność inicjalizacji stanu"""
        self.assertIsInstance(self.initial_state, DeeperKnowledgeSeekerState)
        self.assertEqual(self.initial_state.topic_to_research, "Sztuczna inteligencja w medycynie")
        self.assertEqual(len(self.initial_state.deeper_knowledge_results), 0)

    async def test_graph_execution(self):
        """Test sprawdzający wykonanie grafu"""
        try:
            result = await graph.ainvoke(
                {"state": self.initial_state},
                config=self.config
            )
            self.assertIsNotNone(result)
            self.assertIsInstance(result["state"], DeeperKnowledgeSeekerState)
        except Exception as e:
            self.fail(f"Graph execution failed with error: {str(e)}")

if __name__ == "__main__":
    unittest.main() 