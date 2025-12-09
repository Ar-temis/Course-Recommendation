import time

import dspy
import mlflow
from crec.conversation_memory import MemoryTools, ConversationMemory
from crec.tools.course_ret import course_retriever
from crec.tools.major_ret import major_retriever
from crec.tools.schedule_ret import schedule_retriever
from crec.config import config
from crec.synthesizer import Synthesizer


class AgentSignature(dspy.Signature):
    """You are an university course planning agent that helps students choose their next semester courses.

    If you think the user's query is ambiguous, you are welcome finish tool calling
    and and ask the user to provide more information on what you need to answer their query.

    You are given a list of tools to handle user query, and you should decide the right tool to use in order to
    fulfill users' query.

    Your answer will be fed to the synthesizer, which will produce the final response to the user.

    Available Majors: Arts and Media/Arts, Arts and Media/Media, Global China Studies, Humanities / Creative Writing and Translation, Humanities / Literature, Humanities /Philosophy and Religion, Humanities /World History, Applied Mathematics and Computational Sciences/Computer Science, Applied Mathematics and Computational Sciences/Mathematics, Behavioral Science / Psychology, Behavioral Science / Neuroscience, Computation and Design / Computer Science, Computation and Design / Digital Media, Computation and Design / Social Policy, Cultures and Societies / Cultural Anthropology, Cultures and Societies / Sociology, Data Science, Environmental Science / Biogeochemistry, Environmental Science / Biology, Environmental Science / Chemistry, Environmental Science / Public Policy, Global Health / Biology, Global Health / Public Policy, Materials Science / Chemistry, Materials Science / Physics, Molecular Bioscience / Biogeochemistry, Molecular Bioscience / Biophysics, Molecular Bioscience / Cell and Molecular Biology, Molecular Bioscience / Genetics and Genomics, Molecular Bioscience / Neuroscience, Philosophy, Politics, and Economics / Economic History, Philosophy, Politics, and Economics / Philosophy, Philosophy, Politics, and Economics / Political Science, Philosophy, Politics, and Economics / Public Policy, Quantitative Political Economy / Economics, Quantitative Political Economy /Political Science, Quantitative Political Economy /Public Policy


    Available subject codes: DKU, GERMAN, INDSTU, JAPANESE, KOREAN, MUSIC, SPANISH,
    ARHU, ARTS, BEHAVSCI, BIOL, CHEM, CHINESE, COMPDSGN, COMPSCI, CULANTH, CULMOVE,
    CULSOC, EAP, ECON, ENVIR, ETHLDR, GCHINA, GCULS, GLHLTH, HIST, HUM, INFOSCI,
    INSTGOV, LIT, MATH, MATSCI, MEDIA, MEDIART, NEUROSCI, PHIL, PHYS, PHYSEDU,
    POLECON, POLSCI, PPE, PSYCH, PUBPOL, SOCIOL, SOSC, STATS, USTUD, WOC, RELIG,
    MINITERM
    """

    user_query: str = dspy.InputField()
    conversation_history: str = dspy.InputField(
        desc="Current ongoing conversation history."
    )
    response: str = dspy.OutputField()


class Agent(dspy.Module):
    def __init__(
        self,
        max_iterations: int = 5,
        streaming: bool = False,
        previous_conversation: list = None,
    ):
        """
        Args:
            max_iterations: The maximum rounds of tool call/evaluation the agent
                could execute for a user message. This includes the first round
                of tool calls with the initial user message.
            streaming: If `True`, returns the LLM response as a streaming generator
                for `reponse` returned by synthesizer, else simply return the
                complete response as a string.
            previous_conversation: List of User-Assistant conversation retrieved from the database.
        """

        super().__init__()
        self.streaming = streaming
        self.prev_response = None

        memory_config = {
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": config.mem_col,
                    "path": config.mem_chroma,
                },
            },
            "embedder": {
                "provider": "ollama",
                "config": {"model": config.embedding},
            },
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": config.llm,
                    "temperature": 0.1,
                    "max_tokens": 2500,
                },
            },
        }
        self.memory_tools = MemoryTools(memory_config)
        self.conversation_memory = ConversationMemory()

        # TODO: Conversation history
        try:
            if previous_conversation:
                for conversation in previous_conversation:
                    user, bot = conversation[0], conversation[1]
                    self.conversation_memory.save(
                        role="user",
                        content=user,
                    )
                    self.conversation_memory.save(
                        role="assistant",
                        content=bot,
                    )
        except Exception as e:
            print(f"error encountered in loading conversation: {e}")

        self.agent = dspy.ReAct(
            signature=AgentSignature,
            tools=[
                self.memory_tools.search_memories,
                self.memory_tools.get_all_memories,
                course_retriever,
                major_retriever,
                schedule_retriever,
            ],
            max_iters=max_iterations,
        )

        self.synthesizer = Synthesizer()

    def reset(self):
        self.prev_response = None
        self.conversation_memory = ConversationMemory()

    def _forward(self, user_query: str):
        history = self.conversation_memory.history_str()
        # if self.streaming:
        #     react_streamer = dspy.streamify(
        #         program=self.agent,
        #         stream_listeners=[
        #             dspy.streaming.StreamListener(signature_field_name="response")
        #         ],
        #         async_streaming=False,
        #     )
        #     response_gen = react_streamer(
        #         user_query=user_query,
        #         conversation_history=history,
        #     )
        #     return dspy.Prediction(response=response_gen)
        #
        # else:
        #     response = self.react(
        #         user_query=user_query,
        #         conversation_history=history,
        #     ).response
        #     return dspy.Prediction(response=response)

        intermediate_result = self.agent(
            user_query=user_query, conversation_history=history
        )

        synthesizer_args = {
            "conversation_memory": self.conversation_memory,
            "agent_reasoning": intermediate_result.reasoning,
            "agent_output": intermediate_result.response,
            "current_user_message": user_query,
            "streaming": self.streaming,
        }

        self.prev_response = self.synthesizer(**synthesizer_args)

        return self.prev_response

    def forward(self, user_query: str):
        gen = self._forward(
            user_query,
        )

        response = ""

        if self.streaming:
            first_token = True
            for chunk in gen.response:
                if isinstance(chunk, dspy.streaming.StreamResponse):
                    first_token = False
                    # response += chunk.chunk
                    yield chunk.chunk

                elif isinstance(chunk, dspy.Prediction):
                    response = chunk.response
                    if first_token:
                        yield response
        else:
            response = gen.response
            yield response

        self.conversation_memory.save(
            role="user",
            content=user_query,
        )
        self.conversation_memory.save(
            role="assistant",
            content=response,
        )

        self.memory_tools.store_memory(
            [
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": response},
            ]
        )
        return dspy.Prediction(response)


def main():
    # Tell MLflow about the server URI.
    mlflow.set_tracking_uri("http://127.0.0.1:8889")
    # Create a unique name for your experiment.
    mlflow.set_experiment("Testing")
    mlflow.dspy.autolog()

    lm = dspy.LM(
        model="ollama_chat/" + config.llm,
        api_base=config.llm_url,
        api_key=config.llm_api_key,
        max_tokens=4000,
        temperature=config.llm_temperature,
    )
    dspy.configure(lm=lm)
    # To disable cache:

    # dspy.configure_cache(
    # enable_disk_cache=False,
    # enable_memory_cache=False
    # )

    agent = Agent(
        max_iterations=5,
        streaming=True,
    )

    while True:
        print("*" * 10)
        current_user_message = input("Enter your query: ")
        start_time = time.time()
        responses_gen = agent(
            user_query=current_user_message,
        )
        first_token = True
        print("Response:")
        for r in responses_gen:
            if first_token:
                end_time = time.time()
                print(f"Response delay:{end_time - start_time}")
                first_token = False
            print(r, end="")


if __name__ == "__main__":
    main()
