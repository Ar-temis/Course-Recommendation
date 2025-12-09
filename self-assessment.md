1. Built retrieval-augmented generation (RAG) system with document retrieval (e.g., from a static dataset/ database, or from dynamic web search/scraping) and generation components (10 pts)

2. Used sentence embeddings for semantic similarity or retrieval (5 pts)

    **For both of these points:**
- Document retrieval in: 
    - https://github.com/Ar-temis/Course-Recommendation/blob/59db4ff7e59f2b4dc26ba5cc5f5c690d68daeb6d/crec/ingestion/courses.py#L23-L73

- Generation Components/ how it is fed to the LLM are in: 
    - https://github.com/Ar-temis/Course-Recommendation/blob/59db4ff7e59f2b4dc26ba5cc5f5c690d68daeb6d/crec/tools/course_ret.py#L28-L99

3. Built multi-turn conversation system with context management and history tracking (7 pts)

    - History tracking code can be found here:
        - https://github.com/Ar-temis/Course-Recommendation/blob/59db4ff7e59f2b4dc26ba5cc5f5c690d68daeb6d/crec/conversation_memory.py#L94-L113

    - How it is used is found in:
        - https://github.com/Ar-temis/Course-Recommendation/blob/59db4ff7e59f2b4dc26ba5cc5f5c690d68daeb6d/crec/agent.py#L90-L100
        - https://github.com/Ar-temis/Course-Recommendation/blob/59db4ff7e59f2b4dc26ba5cc5f5c690d68daeb6d/crec/agent.py#L185-L199

4. Used or fine-tuned a transformer language model (7 pts)

    Used GPT-OSS

5. Made API calls to state-of-the-art model (GPT-4, Claude, Gemini) with meaningful integration into your system (5 pts)

    The API calls are abstracted away in DSPy framework, but here is how I set up my API_key for cloud GPT-OSS:
    - https://github.com/Ar-temis/Course-Recommendation/blob/59db4ff7e59f2b4dc26ba5cc5f5c690d68daeb6d/crec/agent.py#L210-L216
    - https://github.com/Ar-temis/Course-Recommendation/blob/59db4ff7e59f2b4dc26ba5cc5f5c690d68daeb6d/app/__init__.py#L61-L68

6. Applied in-context learning with few short examples or chain of thought prompting (5 pts)

    DSPy abstracts away the actual chain of thought prompt, but what it does is that
    it plugs in my inputs and adds the chain-of-thought prompts after my inputs.

    You can see this happening in the analysis tool here:

    The code is here:
    - https://github.com/Ar-temis/Course-Recommendation/blob/95b334eb7df4f6a6c30154f95b3aebda4b197d50/crec/synthesizer.py#L51

7. Completed project individually without a partner (10 pts)

8. Used a significant software framework for applied ML not covered in the class (e.g., instead of PyTorch, used Tensorflow; or used JAX, LangChain, etc. not covered in the class) (5 pts).

    Used DSPy framework, the aim of this framework is to program—not prompt—Foundation Models.

    Also used LangChain for retrievals in here:
    - https://github.com/Ar-temis/Course-Recommendation/blob/95b334eb7df4f6a6c30154f95b3aebda4b197d50/crec/ingestion/major_req_dict.py#L71-L78

9. Implemented production-grade deployment (evidence of at least two considerations such as rate limiting, caching, monitoring, error handling, logging) (10 pts)

    It has a monitoring funclionality using [mlflow](https://mlflow.org/docs/3.0.0rc0/).
    The necessary codes are:
    - https://github.com/Ar-temis/Course-Recommendation/blob/95b334eb7df4f6a6c30154f95b3aebda4b197d50/app/__init__.py#L14-L42

    It has caching also. If you input the same prompt twice, it will use the cached response instead of generating new one.
    This is done through DSPy.

10. Deployed model as functional web application with user interface (10 pts)

    Used flask and basic html to deploy a graphical UI.
    You can find the necessary codes for it in `app`.

11. Implemented agentic system where model outputs trigger automated actions or tool calls (e.g., function calling, database writes, API integrations) (7 pts)

    ReACT agent can be found here:
    - https://github.com/Ar-temis/Course-Recommendation/blob/95b334eb7df4f6a6c30154f95b3aebda4b197d50/crec/agent.py#L104-L114

12. Modular code design with reusable functions and classes rather than monolithic scripts (3 pts)
