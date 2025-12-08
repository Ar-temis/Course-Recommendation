# Course-Recommendation

**Setup:** [SETUP.md](https://github.com/Ar-temis/Course-Recommendation/blob/main/SETUP.md) 

## What it does
Course-Recommendation is a chatbot designed to help you choose majors and courses.

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

Here is a list of commands for a quickstart:
```bash
git clone https://github.com/Ar-temis/Course-Recommendation.git
cd Course-Recommendation

pip install uv
uv venv --python 3.11
source .venv/bin/activate
uv sync
```

> [!IMPORTANT]
> Remember you still need to install [ollama](https://ollama.com/download) and the data necessary from [here](https://duke.box.com/s/0db37aeh6ott2wiaq2wdfyc4m2t7rt9x) .

**Setup data directory:**
```
python3 crec/setup.py
```

## Usage
In the project root folder, run the application full-stack with:

```bash
flask run
```

## Documentation
**WIP**

## Video Links
**WIP** 
