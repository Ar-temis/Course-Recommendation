import dspy

from crec.conversation_memory import ConversationMemory

from crec.config import config

from datetime import date


class SynthesizerSignature(dspy.Signature):
    """
    You are ChatDKU, a helpful, respectful, and honest assistant for students,
    faculty, and staff of, or people interested in Duke Kunshan University (DKU).
    You are created by the DKU Edge Intelligence Lab.
    Duke Kunshan University is a world-class liberal arts institution in Kunshan, China,
    established in partnership with Duke University and Wuhan University.

    Here are basic requirements for scheduling courses:
        There are 2 sessions in a semester.
        In one session, you can have 10 credits worth of courses.
        The minimium amount of credits you can have in a semester is 16.

    You are tasked with answering the **Current User Message**.

    An agent has grabbed everything you need to answer the user message.
    Use the agent's tool results to create an schedule for the student.

    If the agent needs more information from the user, ask the agent's question from the user.

    **Never mention internal tools**:
       - It is **strictly forbidden** to mention your internal processes and tool calls (vector retriever, keyword retriever).
       - Do not reference your internal tool calls (e.g., 'Based on the conversation history', 'Based on vector retriever tool', 'Based on keyword retriever tool', 'According to the vector retriever tool') when answering user query.
    """

    conversation_history: str = dspy.InputField(
        desc=(
            "Previous conversation between user and you, the assistant, in JSON Lines format. "
            "Each line specifies the role and content of the message. "
            "The Current User Message is a continuation of this conversation. "
            "It would be empty if there were no previous conversation."
        ),
        format=lambda x: x,
    )

    agent_trajectory: str = dspy.InputField()
    agent_reasoning: str = dspy.InputField()
    agent_output: str = dspy.InputField()
    current_date: date = dspy.InputField()
    current_user_message: str = dspy.InputField()
    response: str = dspy.OutputField()


class ResponseGen:
    """A generator that uses the DSPY streamify."""

    def __init__(
        self,
        streamer,
    ):
        self.llm_completion_gen = streamer
        self.full_response = ""

    def __iter__(self):
        first_token = True
        for chunk in self.llm_completion_gen:
            if isinstance(chunk, dspy.streaming.StreamResponse):
                first_token = False
                yield chunk.chunk

            if isinstance(chunk, dspy.Prediction):
                self.full_response = chunk.response
                if first_token:
                    yield chunk.response

    def get_full_response(self) -> str:
        # Make sure the entire response is read
        return self.full_response


class Synthesizer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.synthesizer = dspy.Predict(SynthesizerSignature)

    def forward(
        self,
        current_user_message: str,
        conversation_memory: ConversationMemory,
        agent_trajectory: str,
        agent_reasoning: str,
        agent_output: str,
        streaming: bool,
    ):

        synthesizer_args = dict(
            current_user_message=current_user_message,
            conversation_history=conversation_memory.history_str(),
            agent_trajectory=agent_trajectory,
            agent_reasoning=agent_reasoning,
            agent_output=agent_output,
        )
        synthesizer_args["current_date"] = date.today()

        if streaming:
            synthesizer_streamer = dspy.streamify(
                program=self.synthesizer,
                stream_listeners=[
                    dspy.streaming.StreamListener(signature_field_name="response")
                ],
                async_streaming=False,
            )
            if hasattr(config, "tracer"):
                response_gen = ResponseGen(
                    synthesizer_streamer(**synthesizer_args),
                )

            else:
                response_gen = ResponseGen(synthesizer_streamer(**synthesizer_args))
            return dspy.Prediction(response=response_gen)

        else:
            response = self.synthesizer(**synthesizer_args).response
            return dspy.Prediction(response=response)
