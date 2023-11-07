from datetime import date

from decouple import config
from langchain.agents import Tool, AgentExecutor, ZeroShotAgent
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.prompts import PromptTemplate


def ask():
    prompt = "Ask me a question about your business."
    return prompt


def tell():
    prompt = "Tell me something about your business."
    return prompt


def shared(message):
    print(breakdown_question(message))


    template = """This is a conversation between a human and a bot:

    {chat_history}

    Write a summary of the conversation for {input}:
    """

    prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    summary_chain = LLMChain(
        llm=OpenAI(openai_api_key=config("OPENAI_API_KEY")),
        prompt=prompt,
        verbose=True,
        memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
    )

    tools = [
        Tool(
            name="Analyze Inbound",
            func=analyze_inbound,
            description="useful for when you need to break down a question into its parts. The input to this tool should be a string, representing the question you want to break down.",
        ),
        Tool(
            name="Handle ASK",
            func=handle_ask,
            description="useful for handling an ASK. The input to this tool should be a string, representing the ASK.",
        ),
        Tool(
            name="Handle TELL",
            func=handle_tell,
            description="useful for handling a TELL. The input to this tool should be a string, representing the TELL.",
        ),
    ]

    prefix = """You are an assistant for Leo Guinan, who is a senior software engineer for Copy.ai. Your job is to manage his inbound and outbound communications. You have access to the following tools:"""
    suffix = """Begin!"

    {chat_history}
    Question: {input}
    {agent_scratchpad}"""

    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )

    llm_chain = LLMChain(llm=OpenAI(temperature=0, openai_api_key=config("OPENAI_API_KEY")), prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory
    )

    return agent_chain.run(input=message)


def lookup_neighbors():
    neighbors = [
        {
            "name": "ElephantAlpha",
            "address": "doesitmatterwhatthisis?"
        }
    ]
    pass

def record_conversation():
    pass

def breakdown_question(question):
    template = """Here's a question: {input}
    
    What questions need to be answered in order to answer this question?
    
    Respond with a list of questions in JSON format, like this:
    [
    {{
    "question": "What is the business model?",
    }},
    {{
    "question": "What is the target market?",
    }},
    {{
    "question": "What is the value proposition?",
    }},
    ]
        """

    prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    breakdown_chain = LLMChain(
        llm=OpenAI(openai_api_key=config("OPENAI_API_KEY")),
        prompt=prompt,
        verbose=True,
        memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
    )

    return breakdown_chain.run(input=question)


def analyze_inbound(question):
    template = f"""Here's an inbound request: {{input}}

    Your job is to identify all ASKs, TELLs, and RESPONSEs in this request and break them down.
    
    TELL: This is strictly informational in nature. No action needs taken.
    
    ASK: This is a question that needs to be answered or a task that needs to be completed. It may or may not have a due date. If no due date is given, give a rough estimate of when it should be completed. Today
    s date is {date.today()}. If it has dependencies on the other asks, identify those dependencies.
    
    RESPONSE: This is a response to an ASK.


    Respond with the information in JSON format, like this:
    {{{{
    "sender": "<person who sent the message>",
    "date_of_message": "<current date>",
    "asks": [
        {{{{
            "id": "business_model",
            "ask": "What is the business model?",
            "due_date": "<due date>",
            "dependencies": []
        }}}},
        {{{{
            "id": "target_market",
            "ask": "What is the target market?",
            "due_date": "<due date>",
            "dependencies": []
        }}}},
        {{{{
            "id": "value_proposition",
            "ask": "What is the value proposition?",
            "due_date": "<due date>",
            "dependencies": []
        }}}},
    ],
    "tells": [
        {{{{  
            "tell": "A new business is being started, called Copy.ai. It's a SaaS product that provides smart pipes for an organization's communications",
        }}}},
        {{{{
            "tell": "The business model is a subscription model, with a free trial. The target market is small businesses. The value proposition is that it saves time and money for small businesses by automating their communications.",
        }}}}
    ],
    ]
    
    }}}}
    ],
    }}}}
   
        """

    prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    analyze_inbound_chain = LLMChain(
        llm=OpenAI(openai_api_key=config("OPENAI_API_KEY")),
        prompt=prompt,
        verbose=True,
        memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
    )

    return analyze_inbound_chain.run(input=question)


def handle_ask(question):
    template = """Here's an inbound request: {input}

    It's been categorized as an ASK.
    
    Your job is to break this task down into a series of steps. For each step, identify what information is needed to complete that step.

    Respond with the steps in JSON format, like this:
    {{
    "steps": [
    {{
    "step": "Identify the business model",
    "information_needed": ["What's the business model?", "What's the value proposition?", "What's the target market?"],
    }}
    ]
    }}
   
        """

    prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    handle_ask_chain = LLMChain(
        llm=OpenAI(openai_api_key=config("OPENAI_API_KEY")),
        prompt=prompt,
        verbose=True,
        memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
    )

    return handle_ask_chain.run(input=question)

def handle_tell(message):
    # send tell to the right place. Where does it go from here?
    # save conversation context

    print("Message received:", message)

    return "Thanks for letting me know. I'll make a note of it."

