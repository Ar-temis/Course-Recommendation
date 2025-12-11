# Course-Recommendation
Course-Recommendation is a chatbot designed to help you choose majors and courses.
<img width="1244" height="1157" alt="image" src="https://github.com/user-attachments/assets/cab8b08e-a4ed-491f-acbe-1fe13a9b1420" />

**Setup:** [SETUP.md](https://github.com/Ar-temis/Course-Recommendation/blob/main/SETUP.md) 

## What it does

As a student you have to find what courses are available, which ones go together, and which ones you need for you major. 
Finally, you have to schedule them, and if they don't match you find yourself back at square one.

So, what if there was an assistant that just gives you all the available options and you choose from there? 
That's what my AI assistant is ***exactly*** doing for you.

**This assistant can:**
- Find major requirements
- Recommend majors
- Find course prerequisites
- Schedule next semester's courses

## Quickstart
**Please go to [SETUP.md](https://github.com/Ar-temis/Course-Recommendation/blob/main/SETUP.md)** 

In the project root folder, after setting up, you can run the app using:
```bash
# For frontend app:
flask run
```

For **terminal chatting**, you have to create two terminal instances.
One for mlflow, and one for the agent.

Terminal one:
```bash
mlflow server --backend-store-uri sqlite:///mydb.sqlite -p 8889
```
Terminal two:
```bash
python3 crec/agent.py
```
## Documentation
<img width="709" height="716" alt="image" src="https://github.com/user-attachments/assets/663b17b6-d2a7-42a7-ae49-6ad4bd1f4a1c" />

There are 4 different retrievers for the agent:
- Major retriever: Which retrieves major requirements from a dictionary, using soft keyword matching
- Course retriever: Retrieves course info such as description and prerequisites, uses chromaDB vector store and metadata searching
- Schedule Retriever: Retrieves next semester's schedule for specific courses or majors
- Memory retriever: Searches for long term memory to get specific info about the user.

## Video Links
**Primary Demo:** https://youtu.be/8glZdfNl_Uk 

**Technical Demo:** https://youtu.be/U8BUoQR8Gho

