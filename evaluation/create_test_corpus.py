"""
创建 20 篇 AI Agent 论文的文本测试集
基于公开论文摘要和核心方法整理
"""
from pathlib import Path

SAVE_DIR = Path(__file__).parent / "test_corpus"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

PAPERS = {
    "2210.03629_ReAct.txt": """
ReAct: Synergizing Reasoning and Acting in Language Models
Authors: Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao
Published: ICLR 2023

Abstract:
Large language models (LLMs) have demonstrated impressive capabilities across tasks requiring reasoning and decision-making. However, reasoning (e.g., chain-of-thought prompting) and acting (e.g., action plan generation) have primarily been studied as separate topics. In this paper, we explore the use of LLMs to generate both reasoning traces and task-specific actions in an interleaved manner, allowing for greater synergy between the two.

Core Method:
ReAct (Reasoning + Acting) is a prompting paradigm that enables LLMs to generate interleaved thoughts and actions. The key insight is to extend the action space to include both task-specific actions and natural language reasoning traces (thoughts). 

The ReAct framework follows a Thought-Action-Observation loop:
1. Thought: The model reasons about the current state and plans next steps
2. Action: The model performs an action (e.g., search, lookup, navigate)
3. Observation: The model receives feedback from the environment

This allows the model to:
- Induce, track, and update action plans through reasoning
- Handle exceptions and recover from errors
- Interface with external sources (knowledge bases, environments) to gather information
- Avoid hallucination by grounding reasoning in external observations

Experiments:
ReAct was evaluated on four diverse benchmarks:
1. HotpotQA (multi-hop question answering): ReAct outperformed pure reasoning and pure acting baselines, achieving better factuality
2. FEVER (fact verification): ReAct achieved state-of-the-art performance with improved interpretability
3. ALFWorld (text-based games): ReAct achieved 34% higher success rate than baseline methods
4. WebShop (online shopping): ReAct outperformed imitation learning baselines

Key Findings:
- ReAct combines the strengths of chain-of-thought reasoning (plan generation) and acting (information gathering)
- The interleaved format makes the model's decision process more interpretable
- ReAct is more robust to errors than pure reasoning or pure acting approaches
- Human evaluators preferred ReAct's outputs for their transparency and correctness
""",

    "2303.11366_Reflexion.txt": """
Reflexion: Language Agents with Verbal Reinforcement Learning
Authors: Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao
Published: NeurIPS 2023

Abstract:
Large language models (LLMs) have been increasingly used to interact with external environments as goal-driven agents. However, it remains challenging for these language agents to quickly and efficiently learn from trial-and-error as traditional reinforcement learning methods require extensive training samples and expensive model fine-tuning. We propose Reflexion, a novel framework to reinforce language agents not by updating weights, but instead through linguistic feedback.

Core Method:
Reflexion is a framework that enables language agents to learn from failures through verbal self-reflection, without updating model weights. The key innovation is replacing scalar reward signals with natural language feedback.

The Reflexion architecture consists of three components:
1. Actor: Generates task solutions based on observations and long-term memory
2. Evaluator: Scores the actor's outputs and provides feedback signals
3. Self-Reflection: Generates verbal reinforcement cues based on task feedback

The learning process:
1. The Actor attempts a task and produces a trajectory
2. The Evaluator assesses the outcome (success/failure, scalar reward)
3. The Self-Reflection module generates natural language reflection on what went wrong
4. The reflection is stored in an episodic memory buffer
5. In subsequent trials, the Actor uses accumulated reflections to improve decision-making

Key Features:
- No gradient updates required - learning happens purely through context
- Supports various feedback types: scalar values, free-form language, external or internal signals
- Maintains persistent memory across multiple trials
- Can be combined with any base agent architecture (ReAct, chain-of-thought, etc.)

Experiments:
Reflexion was evaluated on three domains:
1. Decision-Making (ALFWorld): Achieved 91% success rate, significantly outperforming ReAct baseline (73%)
2. Reasoning (HotpotQA): Improved accuracy by 13% over baseline through iterative self-correction
3. Programming (HumanEval, LeetCode): Achieved state-of-the-art pass@1 rates, with 80% on HumanEval and 91% on LeetCode Hard

Key Findings:
- Verbal reinforcement is more efficient than scalar rewards for language agents
- Self-reflection enables rapid learning from just a few failures
- The approach is model-agnostic and can be applied to any LLM
- Reflexion demonstrates emergent generalization across related tasks
""",

    "2302.04761_Toolformer.txt": """
Toolformer: Language Models Can Teach Themselves to Use Tools
Authors: Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, Thomas Scialom
Published: NeurIPS 2023

Abstract:
Language models exhibit remarkable abilities but struggle with basic functionalities such as arithmetic or factual lookup, where much simpler and smaller models excel. In this paper, we show that LMs can teach themselves to use external tools via simple APIs and achieve the best of both worlds. We introduce Toolformer, a model trained to decide which APIs to call, when to call them, what arguments to pass, and how to best incorporate the results into future token prediction.

Core Method:
Toolformer is a self-supervised approach for teaching language models to use external tools. The key innovation is that the model generates its own training data for tool use, without requiring human annotations.

The training process has three stages:
1. Sampling API Calls:
   - Given a plain text dataset, the model uses few-shot prompting to annotate potential API call positions
   - For each position, the model generates candidate API calls with arguments
   - Multiple candidates are sampled per position

2. Executing API Calls:
   - Each candidate call is actually executed against the corresponding tool
   - Tools include: question answering, calculator, Wikipedia search, translation, calendar
   - Real results are obtained from each API call

3. Filtering by Self-Supervised Loss:
   - For each candidate call, compare the loss of predicting subsequent tokens with and without the API result
   - Keep only calls that reduce the loss (i.e., the tool result actually helps prediction)
   - This creates a high-quality dataset of useful tool calls

After filtering, the model is fine-tuned on the filtered dataset.

Key Features:
- Fully self-supervised: no human annotation required
- Tool-agnostic: can learn to use any API
- Decides when and how to use tools autonomously
- Maintains general language modeling abilities while gaining tool proficiency

Experiments:
Toolformer was evaluated on various downstream tasks:
- Mathematical reasoning: Significant improvement on GSM8K and other math benchmarks
- Factual QA: Reduced hallucination through Wikipedia lookup
- Multi-step reasoning: Better performance on tasks requiring external information
- The model learned to use tools appropriately without explicit instruction

Key Findings:
- Self-supervised filtering is crucial - random tool calls hurt performance
- The model learns to use tools only when genuinely helpful
- Tool use transfers to tasks not seen during training
- Smaller models with tools can outperform larger models without tools
""",

    "2304.03442_Generative_Agents.txt": """
Generative Agents: Interactive Simulacra of Human Behavior
Authors: Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein
Published: UIST 2023

Abstract:
Believable proxies of human behavior can empower interactive applications ranging from immersive environments to rehearsal spaces for interpersonal communication to prototyping tools. In this paper, we introduce generative agents, computational software agents that simulate believable human behavior. Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on days past as they plan the next day.

Core Method:
Generative agents are LLM-powered agents that simulate believable human behavior in a sandbox environment. The architecture includes three key components:

1. Memory Stream:
   - A comprehensive record of the agent's experiences
   - Each memory has a creation timestamp, access timestamp, and importance score
   - Stores observations, reflections, and plans
   - Retrieval is based on recency, importance, and relevance

2. Reflection Mechanism:
   - Agents periodically reflect on their experiences
   - Reflections are higher-level abstract thoughts generated from memories
   - Reflection is triggered when the sum of importance scores of recent events exceeds a threshold
   - Reflections themselves become memories, enabling hierarchical reasoning

3. Planning and Reacting:
   - Agents create daily plans based on their characteristics and past experiences
   - Plans can be revised based on new observations
   - Agents react to unexpected events in their environment
   - Dialogue is generated based on the agent's memories and the conversation history

The agent architecture supports:
- Perception of the environment
- Memory retrieval and synthesis
- Reflection and abstract thinking
- Long-term and short-term planning
- Natural conversation with other agents

Experiments:
The system was implemented as a 25-agent simulation in a Smallville-style town:
- Agents exhibited emergent social behaviors: information diffusion, relationship formation, coordinated activities
- A Valentine's Day party invitation spread through the agent social network
- Agents formed opinions about each other based on interactions
- Human evaluators found generative agents more believable than baselines (no reflection, no planning, no memory)

Key Findings:
- The memory stream is critical for coherent behavior over time
- Reflection enables agents to form higher-level inferences
- Planning creates realistic daily routines
- Inter-agent communication leads to emergent social dynamics
- The architecture generalizes to different personalities and scenarios
""",

    "2308.11432_LLM_Agent_Survey.txt": """
A Survey on Large Language Model based Autonomous Agents
Authors: Lei Wang, Chen Ma, Xueyang Feng, Zeyu Zhang, Hao Yang, Jingsen Zhang, Jiakai Tang, Xu Chen, Yankai Lin, Wayne Xin Zhao, Zhewei Wei, Ji-Rong Wen
Published: 2023

Abstract:
Autonomous agents have long been a research focus in artificial intelligence. With the emergence of large language models (LLMs), there has been a surge of interest in LLM-based autonomous agents due to their impressive performance. This paper provides a comprehensive survey of LLM-based autonomous agents, covering their construction, application, and evaluation.

Core Framework:
The survey proposes a unified framework for LLM-based autonomous agents, consisting of four modules:

1. Profile Module:
   - Defines the agent's identity, role, and characteristics
   - Can be hand-crafted or automatically generated
   - Includes personality, background, expertise, and goals
   - Enables role-specific behavior and domain adaptation

2. Memory Module:
   - Sensory memory: brief storage of immediate perceptions
   - Short-term memory: working memory for current task context
   - Long-term memory: persistent storage of past experiences
   - Memory operations: writing, reading, updating, forgetting
   - Memory types: textual, visual, multimodal

3. Planning Module:
   - Planning with feedback: iterative refinement based on environment feedback
   - Planning without feedback: decomposition and reasoning without external feedback
   - Techniques: chain-of-thought, tree-of-thoughts, task decomposition
   - Subgoal ordering and dependency management

4. Action Module:
   - Action formulation: translating decisions into executable actions
   - Tool use: calling external APIs, functions, and services
   - Multi-modal actions: text, code, image, speech
   - Action execution and environment interaction

Agent Classification:
The survey categorizes agents by:
- Single-agent vs. multi-agent systems
- LLM-centric vs. LLM-as-brain architectures
- Task-oriented vs. simulation-oriented agents
- Domain-specific vs. general-purpose agents

Applications:
The survey covers applications in:
- Social sciences: psychology, sociology, economics simulations
- Natural science: research assistance, experiment design, data analysis
- Engineering: software development, system design, testing
- Creative work: writing, art, music, game design
- Practical applications: customer service, education, healthcare

Evaluation:
Evaluation dimensions include:
- Task performance: accuracy, completion rate, efficiency
- Agent capabilities: reasoning, planning, memory, tool use
- Social behaviors: cooperation, communication, role-playing
- Safety and alignment: helpfulness, harmlessness, honesty

Key Challenges:
- Context window limitations for long-term memory
- Hallucination and factual consistency
- Evaluation standardization
- Computational cost and efficiency
- Safety and ethical considerations
""",

    "2308.03688_AgentBench.txt": """
AgentBench: Evaluating LLMs as Agents
Authors: Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, Hangliang Ding, Kaiwen Men, Kejuan Yang, et al.
Published: ICLR 2024

Abstract:
Large language models are exhibiting an increasing number of capabilities, and are being used in increasingly complex real-world applications. However, existing LLM benchmarks mostly evaluate their capabilities in a multi-turn style, which is not suitable for evaluating LLMs as agents. In this paper, we present AgentBench, the first benchmark to evaluate LLMs as agents in a multi-turn, open-ended, and interactive environment.

Core Method:
AgentBench is a comprehensive benchmark designed to evaluate LLMs as autonomous agents. It consists of 8 distinct environments that test different agent capabilities:

1. Operating System (OS):
   - Agents interact with a Linux terminal
   - Tasks: file operations, system administration, command execution
   - Evaluates: tool use, planning, error recovery

2. Database (DB):
   - Agents interact with a database via SQL
   - Tasks: query construction, data manipulation, schema understanding
   - Evaluates: logical reasoning, tool proficiency

3. Knowledge Graph (KG):
   - Agents query a knowledge graph
   - Tasks: multi-hop reasoning, entity resolution
   - Evaluates: structured reasoning, information retrieval

4. Digital Card Game (DCG):
   - Agents play a strategy card game
   - Tasks: resource management, long-term planning, opponent modeling
   - Evaluates: strategic thinking, decision-making under uncertainty

5. Lateral Thinking Puzzles (LTP):
   - Agents solve yes/no puzzles
   - Tasks: information gathering, hypothesis testing
   - Evaluates: creative reasoning, question formulation

6. Household Tasks (Housekeeping):
   - Agents control a simulated household robot
   - Tasks: object manipulation, spatial reasoning
   - Evaluates: embodied intelligence, planning

7. Web Shopping (WebShop):
   - Agents navigate an e-commerce website
   - Tasks: product search, attribute matching, purchase decisions
   - Evaluates: web interaction, goal achievement

8. Web Browsing (WebBrowsing):
   - Agents browse the web to find information
   - Tasks: search, navigation, information extraction
   - Evaluates: internet navigation, research skills

Evaluation Metrics:
- Success rate: percentage of tasks completed
- Average reward: cumulative score across episodes
- Efficiency: number of steps/time to complete tasks
- Error recovery: ability to handle failures

Key Findings:
- There is a significant performance gap between API-based models and open-source models
- GPT-4 consistently outperforms other models across environments
- Agent performance varies widely across different environments
- Most models struggle with long-horizon tasks requiring sustained planning
- Tool use and error recovery are common weaknesses
- The benchmark reveals that LLM agents are still far from human-level performance

The benchmark provides a standardized way to measure progress in LLM agent development.
""",

    "2308.00352_MetaGPT.txt": """
MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework
Authors: Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu Zheng, Yuheng Cheng, Ceyao Zhang, Jinlin Wang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, et al.
Published: ICLR 2024

Abstract:
We introduce MetaGPT, an innovative framework that incorporates efficient human workflows as a meta programming approach into LLM-based multi-agent collaboration. Specifically, MetaGPT encodes Standardized Operating Procedures (SOPs) into prompts to enhance structured coordination. Subsequently, it mandates modular outputs, empowering agents with domain expertise comparable to human professionals, to validate and refine outputs using executable code.

Core Method:
MetaGPT is a multi-agent framework that simulates a software company's workflow. The core philosophy is "Code = SOP(Team)" - software is produced by a team following standardized operating procedures.

Key Components:
1. Role-Based Agents:
   - Product Manager: writes PRD (Product Requirements Document)
   - Architect: designs system architecture and APIs
   - Project Manager: breaks down tasks and creates WBS
   - Engineer: writes code based on task specifications
   - QA Engineer: tests code and reports bugs
   - Each role has specific profile, goals, and constraints

2. Standard Operating Procedures (SOP):
   - SOP = Role + Action + Sequence + Deliverable
   - Defines the order of operations and handoffs between roles
   - Each role observes upstream output and produces downstream input
   - Encodes human best practices into structured workflows

3. Knowledge Sharing:
   - Shared message pool for inter-agent communication
   - Publish-subscribe pattern for role-specific message filtering
   - Each agent subscribes to relevant message types
   - Reduces information overload and improves focus

4. Modular Outputs:
   - Each role produces structured, standardized documents
   - Outputs are validated and can be parsed programmatically
   - Enables automated quality checking and refinement

The Software Development Workflow:
1. User requirement → Product Manager → PRD
2. PRD → Architect → System Design Document + API spec
3. Design → Project Manager → Task breakdown + dependencies
4. Tasks → Engineer → Code implementation
5. Code → QA Engineer → Testing + bug reports
6. Bug fixes → Engineer → Final code

Experiments:
MetaGPT was evaluated on software development tasks:
- Generated complete, runnable software projects from one-line requirements
- Achieved 82% task completion rate on complex development tasks
- Outperformed single-agent and other multi-agent baselines
- Produced more structured and maintainable code
- The SOP approach reduced hallucination and cascading errors

Key Findings:
- SOP-based coordination significantly improves multi-agent performance
- Role specialization leads to higher quality outputs
- Structured document handoffs prevent information loss
- The framework generalizes beyond software to other domains
- MetaGPT demonstrates that human organizational principles can be effectively transferred to AI teams
""",

    "2307.07924_ChatDev.txt": """
ChatDev: Communicative Agents for Software Development
Authors: Chen Qian, Wei Liu, Chi-Min Chan, Yujie Ren, Wensi Ai, Yuyu Zhang, Jie Fu, Tao Feng, Hung-Yi Lee, Weizhu Chen
Published: ICLR 2024

Abstract:
The development of software engineering has evolved through various paradigms, from structured programming to object-oriented design. However, the fundamental process of software development remains largely human-centric. In this paper, we introduce ChatDev, a novel chat-powered software development framework that leverages multiple communicative agents to automate the software development process.

Core Method:
ChatDev is a multi-agent framework that simulates a software development company through natural language communication. The framework organizes agents into different roles that collaborate through chat.

Agent Roles:
1. Chief Executive Officer (CEO):
   - Strategic decision making
   - Task prioritization and resource allocation
   - Final approval of deliverables

2. Chief Technology Officer (CTO):
   - Technical architecture decisions
   - Technology stack selection
   - Code review and quality oversight

3. Programmer:
   - Writes implementation code
   - Follows design specifications
   - Fixes bugs and issues

4. Code Reviewer:
   - Reviews code for quality and correctness
   - Provides feedback and suggestions
   - Ensures coding standards

5. Tester:
   - Creates and runs test cases
   - Identifies bugs and issues
   - Verifies bug fixes

6. Art Designer (for GUI applications):
   - Designs user interface
   - Creates visual assets
   - Ensures usability

Development Phases:
1. Design Phase:
   - CEO and CTO discuss requirements
   - Determine technology stack and architecture
   - Produce design document

2. Coding Phase:
   - Programmer writes code based on design
   - Code Reviewer provides feedback
   - Iterative refinement through chat

3. Testing Phase:
   - Tester runs the code
   - Reports bugs and issues
   - Programmer fixes problems
   - Iterative until tests pass

4. Documentation Phase:
   - Generate README and usage instructions
   - Document API and architecture
   - Final delivery

Communication Mechanism:
- Agents communicate through structured chat messages
- Each message has a sender, receiver, and content
- Agents can ask questions, provide feedback, request changes
- The chat history serves as shared memory

Experiments:
ChatDev was evaluated on various software development tasks:
- Successfully generated complete, runnable applications
- Average development time: under 7 minutes per project
- Produced games, tools, and web applications
- Human evaluation showed high user satisfaction
- The iterative chat-based approach improved code quality

Key Findings:
- Communicative agents can effectively collaborate on complex tasks
- Role specialization improves output quality
- Natural language communication enables flexible coordination
- The chat-based approach is more flexible than rigid workflows
- ChatDev demonstrates the potential of AI-powered software development
""",

    "2303.17760_CAMEL.txt": """
CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society
Authors: Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, Yining Wang, Jiri Hron, Faisal Shboul, Mohammad Tuqan, Arsalan Ansari, Bernard Ghanem
Published: NeurIPS 2023

Abstract:
The rapid advancement of large language models has led to growing interest in autonomous agents and their potential to solve complex tasks. However, developing agents that can effectively collaborate and communicate remains a challenge. In this paper, we propose CAMEL (Communicative Agents for Mind Exploration), a framework that enables communicative agents to collaborate and explore the capabilities of large language models.

Core Method:
CAMEL is a framework for studying multi-agent collaboration through role-playing communication. The key innovation is the "Inception Prompting" technique that enables agents to assume specific roles and collaborate effectively.

Key Components:
1. Role-Playing Framework:
   - AI Assistant: helps the AI User complete tasks
   - AI User: gives instructions to the AI Assistant
   - Task Specifier: clarifies and specifies the task
   - Each agent has a distinct role and perspective

2. Inception Prompting:
   - A technique to assign roles and set the stage for collaboration
   - The prompt establishes the relationship between agents
   - Includes role definitions, communication protocols, and constraints
   - Ensures agents stay in character and collaborate productively

3. Communication Protocol:
   - Structured message format for agent interaction
   - Each message includes role, content, and instructions
   - Agents take turns responding to each other
   - The conversation continues until task completion

4. Task Specification:
   - A Task Specifier agent expands high-level ideas into detailed tasks
   - Translates vague requirements into concrete objectives
   - Ensures both agents share a common understanding

Agent Societies:
CAMEL explores different agent society configurations:
- AI Society: collaboration between AI Assistant and AI User
- Code Society: specialized agents for software development
- Misalignment Society: studying potential misalignment scenarios
- Domain-specific societies: medicine, law, education, etc.

Experiments:
CAMEL was evaluated on various collaborative tasks:
- Successfully completed complex tasks through agent collaboration
- Demonstrated emergent problem-solving capabilities
- Showed that role-playing enables effective division of labor
- The framework revealed both capabilities and limitations of LLM agents
- Provided insights into agent communication patterns and failure modes

Key Findings:
- Inception prompting is effective for establishing productive agent collaboration
- Role-playing enables agents to leverage different perspectives
- Multi-agent communication can lead to emergent capabilities
- The framework is useful for studying LLM capabilities and limitations
- CAMEL provides a testbed for exploring agent society dynamics
- The approach can be extended to various domains and task types
""",

    "2303.17580_HuggingGPT.txt": """
HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face
Authors: Yongliang Shen, Kaitao Song, Xu Tan, Dongsheng Li, Weiming Lu, Yueting Zhuang
Published: NeurIPS 2023

Abstract:
Solving complicated AI tasks with different domains and modalities is a key step toward advanced artificial intelligence. While there are abundant AI models available for different domains and modalities, they cannot handle complicated AI tasks. Considering large language models exhibit exceptional ability in language understanding, generation, interaction, and reasoning, we advocate that LLMs could act as a controller to manage existing AI models to solve complicated AI tasks.

Core Method:
HuggingGPT is a framework that uses ChatGPT as a controller to orchestrate expert models from Hugging Face for solving complex AI tasks. The system connects language understanding with multimodal AI capabilities.

Architecture:
HuggingGPT follows a four-stage pipeline:

1. Task Planning:
   - ChatGPT parses the user request
   - Decomposes complex tasks into subtasks
   - Determines the order and dependencies of subtasks
   - Handles both single-step and multi-step tasks

2. Model Selection:
   - For each subtask, ChatGPT selects appropriate expert models
   - Models are chosen based on their function descriptions
   - The system matches task requirements to model capabilities
   - Multiple models can be selected for a single subtask

3. Task Execution:
   - Selected models are executed with appropriate inputs
   - Results are collected and passed to subsequent subtasks
   - The system handles different input/output modalities
   - Execution is managed according to task dependencies

4. Response Generation:
   - ChatGPT integrates all execution results
   - Generates a natural language response for the user
   - Includes explanations and references to model outputs
   - Handles failures and provides alternative approaches

Supported Modalities and Tasks:
- Text: classification, summarization, translation, question answering
- Image: generation, classification, object detection, segmentation
- Audio: speech recognition, speech synthesis, audio classification
- Video: generation, classification, captioning
- Cross-modal: text-to-image, image-to-text, visual question answering

Key Features:
- Leverages hundreds of expert models from Hugging Face
- No fine-tuning required - uses in-context learning
- Supports complex multi-step, multi-modal tasks
- Automatic model selection and orchestration
- Handles task dependencies and execution order

Experiments:
HuggingGPT was evaluated on various complex tasks:
- Multi-modal question answering
- Image generation and editing pipelines
- Audio-visual content creation
- Complex reasoning tasks requiring multiple models
- The system successfully completed tasks requiring coordination of 2-5 expert models

Key Findings:
- LLMs can effectively serve as controllers for expert model ecosystems
- Language is a universal interface for connecting diverse AI models
- The approach enables solving tasks beyond any single model's capability
- Model description quality is critical for effective selection
- The framework demonstrates the potential of model collaboration
""",

    "2305.16291_Voyager.txt": """
Voyager: An Open-Ended Embodied Agent with Large Language Models
Authors: Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, Anima Anandkumar
Published: NeurIPS 2023

Abstract:
We introduce Voyager, the first LLM-powered embodied lifelong learning agent in Minecraft that continuously explores the world, acquires diverse skills, and makes novel discoveries without human intervention. Voyager consists of three key components: an automatic curriculum that maximizes exploration, an ever-growing skill library of executable code for storing and retrieving complex behaviors, and a new iterative prompting mechanism that incorporates environment feedback, execution errors, and self-verification for program improvement.

Core Method:
Voyager is an autonomous agent for Minecraft that uses GPT-4 to learn and improve continuously. It addresses the challenge of open-ended learning in embodied environments.

Three Key Components:

1. Automatic Curriculum:
   - Proposes increasingly difficult tasks based on the agent's current capabilities
   - Maximizes exploration by targeting novel items and locations
   - Tasks are generated based on game progression and agent state
   - The curriculum adapts to what the agent has already mastered
   - Encourages discovery of new biomes, resources, and crafting recipes

2. Skill Library:
   - Stores learned skills as executable JavaScript code
   - Each skill is a function that can be composed with other skills
   - Skills are indexed by embedding for semantic retrieval
   - New skills are added to the library as they are learned
   - Complex behaviors are built by composing simpler skills
   - The library grows monotonically over time

3. Iterative Prompting Mechanism:
   - GPT-4 generates code for proposed tasks
   - Code is executed in the Minecraft environment
   - Environment feedback (success/failure, state changes) is collected
   - Execution errors are fed back to GPT-4 for debugging
   - Self-verification: the agent checks if the task was completed
   - The process repeats until success or maximum iterations

Key Features:
- Lifelong learning: skills accumulate and improve over time
- No human intervention: fully autonomous exploration
- Code as actions: executable programs are more reusable than natural language
- Skill composition: complex behaviors from simple primitives
- Contextual learning: adapts to specific world seeds and environments

Experiments:
Voyager was evaluated in Minecraft:
- Discovered 63 unique items in 160 minutes, 3.3x more than baselines
- Achieved 2.3x faster progression through tech tree
- Successfully learned and composed 30+ distinct skills
- Generalized to new worlds and tasks better than baselines
- Demonstrated emergent behaviors like building shelters and farming
- Outperformed ReAct, Reflexion, and other baselines significantly

Key Findings:
- Code-based skill representation enables better reuse and composition
- Automatic curriculum drives efficient exploration
- Iterative debugging with environment feedback is crucial
- Skill library enables transfer learning across tasks
- The approach demonstrates the potential of LLM-powered lifelong learning
""",

    "2305.10601_Tree_of_Thoughts.txt": """
Tree of Thoughts: Deliberate Problem Solving with Large Language Models
Authors: Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Thomas L. Griffiths, Yuan Cao, Karthik Narasimhan
Published: NeurIPS 2023

Abstract:
Language models are increasingly being deployed for general problem solving across a wide range of tasks, but are still confined to token-level, left-to-right decision-making processes during inference. This means they can fall short in tasks that require exploration, strategic lookahead, or where initial decisions play a pivotal role. To surmount these challenges, we introduce a new framework for language model inference, Tree of Thoughts (ToT), which generalizes over the popular Chain of Thought approach to prompting language models.

Core Method:
Tree of Thoughts (ToT) is a framework that enables LLMs to explore multiple reasoning paths simultaneously, rather than following a single linear chain of thought. It allows deliberate problem solving through search over a tree of thoughts.

Key Concepts:
1. Thought as a Unit:
   - A "thought" is a coherent language sequence that serves as an intermediate step
   - Each thought represents a partial solution or reasoning step
   - Thoughts are generated and evaluated by the LLM
   - Multiple thoughts can be explored in parallel

2. Tree Structure:
   - Root: initial problem or input
   - Branches: possible next thoughts or reasoning steps
   - The tree grows as the model explores alternatives
   - Leaves: complete solutions or dead ends

3. Search Algorithms:
   - BFS (Breadth-First Search): explore level by level, maintain best candidates
   - DFS (Depth-First Search): explore one path deeply, backtrack when stuck
   - The search algorithm can be chosen based on task characteristics

4. Thought Generation:
   - Given a state, generate candidate next thoughts
   - Can use sampling (diverse generation) or proposal (structured generation)
   - The number of candidates is a controllable parameter

5. State Evaluation:
   - Evaluate how promising each thought/state is
   - Use value function or LLM self-evaluation
   - Evaluation can be per-state (how good is this partial solution?)
   - Or per-vote (multiple samples, majority vote)

The ToT Process:
1. Decompose the problem into thought steps
2. Generate candidate thoughts at each step
3. Evaluate candidates using the LLM
4. Search (BFS/DFS) to explore promising paths
5. Output the best complete solution

Experiments:
ToT was evaluated on three tasks requiring deliberate planning:
1. Game of 24: ToT achieved 74% success rate vs 4% for chain-of-thought
2. Creative Writing: ToT produced more coherent and high-quality stories
3. Mini Crosswords: ToT achieved 60% word-level success vs 16% for CoT

Key Findings:
- ToT significantly outperforms chain-of-thought on tasks requiring planning
- The ability to backtrack and explore alternatives is crucial
- LLM self-evaluation works surprisingly well for guiding search
- ToT makes the model's reasoning process more transparent
- The framework is general and can be applied to many problem types
- There is a trade-off between exploration breadth and computational cost
""",

    "2305.04091_Plan_and_Solve.txt": """
Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models
Authors: Lei Wang, Wanyu Xu, Yihuai Lan, Zhiqiang Hu, Roy Ka-Wei Lee, Ee-Peng Lim
Published: ACL 2023

Abstract:
Large language models have shown impressive performance on various tasks. However, their reasoning abilities are still limited, especially for complex tasks that require multi-step reasoning. Chain-of-thought (CoT) prompting has been proposed to improve reasoning by generating intermediate reasoning steps. However, CoT prompting requires manually crafted examples, which is time-consuming and may not generalize well. In this paper, we propose Plan-and-Solve (PS) prompting, a zero-shot prompting strategy that improves upon zero-shot CoT.

Core Method:
Plan-and-Solve prompting is a zero-shot prompting technique that improves multi-step reasoning by explicitly separating planning and execution. It addresses the limitations of standard zero-shot chain-of-thought ("Let's think step by step").

The PS Prompting Framework:
1. Planning Phase:
   - First, the model generates a plan to solve the problem
   - The plan breaks the problem into smaller sub-tasks
   - This provides a structured approach before diving into details
   - The plan serves as a roadmap for the solution

2. Solving Phase:
   - Then, the model executes the plan step by step
   - Each sub-task is addressed according to the plan
   - Intermediate results are computed and tracked
   - The final answer is derived from the completed steps

The standard PS prompt:
"Let's first understand the problem and devise a plan to solve the problem. Then, let's carry out the plan and solve the problem step by step."

PS+ Variant:
An enhanced version that adds more specific instructions:
- Pay attention to calculation details
- Extract relevant variables and their values
- Be careful about units and conversions
- Double-check calculations

Key Features:
- Zero-shot: no example demonstrations required
- Explicit planning before execution
- Reduces calculation errors and missing steps
- More structured than standard CoT
- Easy to implement - just a different prompt template

Why PS Works Better than Zero-Shot CoT:
1. Planning reduces missing steps - the model first outlines what needs to be done
2. Separation of concerns - planning and execution are distinct phases
3. Better organization - the solution follows a logical structure
4. Reduced hallucination - the plan constrains the reasoning space
5. Improved accuracy - explicit planning catches errors early

Experiments:
Plan-and-Solve was evaluated on mathematical reasoning benchmarks:
- GSM8K: PS achieved 62.7% vs 58.5% for zero-shot CoT
- MultiArith: PS achieved 94.3% vs 92.0% for zero-shot CoT
- AddSub: PS achieved 87.5% vs 84.3% for zero-shot CoT
- SVAMP: PS achieved 82.1% vs 78.6% for zero-shot CoT
- PS+ (with more detailed instructions) achieved even higher performance

Key Findings:
- Explicit planning significantly improves zero-shot reasoning
- The plan-then-execute structure reduces errors
- PS is a simple drop-in replacement for "Let's think step by step"
- The improvement is consistent across different model sizes
- PS+ with detailed instructions further enhances performance
- The approach is particularly effective for multi-step arithmetic problems
""",

    "2203.11171_Self_Consistency.txt": """
Self-Consistency Improves Chain of Thought Reasoning in Language Models
Authors: Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, Sharan Narang, Aakanksha Chowdhery, Denny Zhou
Published: ICLR 2023

Abstract:
We explore a simple ensemble strategy, self-consistency, that significantly improves the reasoning accuracy of large language models. The approach involves sampling a diverse set of reasoning paths instead of only taking the greedy one, and then selecting the most consistent answer by marginalizing out the sampled reasoning paths. Self-consistency leverages the intuition that a complex reasoning problem typically admits multiple different ways of thinking leading to its unique correct answer.

Core Method:
Self-Consistency is a decoding strategy that improves chain-of-thought reasoning by sampling multiple reasoning paths and taking a majority vote on the final answer.

The Self-Consistency Process:
1. Prompt with Chain-of-Thought:
   - Use standard CoT prompting with examples
   - Instead of greedy decoding, use sampling (temperature > 0)
   - Generate multiple diverse reasoning paths

2. Sample Diverse Reasoning Paths:
   - Generate k different completions for the same problem
   - Each completion may use different reasoning steps
   - Sampling introduces diversity in approaches
   - Typical k values: 5, 10, 20, 40

3. Extract Final Answers:
   - Parse the final answer from each reasoning path
   - Answers may be numerical, multiple choice, or short text
   - Handle formatting variations in answers

4. Majority Vote:
   - Count the frequency of each answer
   - Select the most common answer as the final result
   - This is equivalent to marginalizing over reasoning paths
   - The intuition: correct answers are more likely to be reached consistently

Key Features:
- No additional training required - purely a decoding strategy
- Works with any CoT prompt
- Improves accuracy without changing the model
- Provides robustness against reasoning errors
- The diversity of paths naturally handles different solution approaches

Why Self-Consistency Works:
- Correct reasoning paths tend to converge on the same answer
- Incorrect paths may produce different wrong answers
- Majority voting cancels out random errors
- The approach leverages the "wisdom of crowds" within one model
- Sampling explores alternative solution methods

Experiments:
Self-Consistency was evaluated on various reasoning benchmarks:
- GSM8K: Improved from 57.2% to 74.4% (with k=40)
- SVAMP: Improved from 79.1% to 86.6%
- AQuA: Improved from 34.5% to 44.2%
- StrategyQA: Improved from 70.2% to 75.2%
- ARC-Challenge: Improved from 85.2% to 87.5%
- Consistent improvements across all benchmarks

Key Findings:
- Self-consistency significantly improves CoT reasoning
- The improvement increases with more samples (diminishing returns)
- The method is most effective for complex multi-step problems
- It works across different model sizes and architectures
- Self-consistency can reveal uncertainty - if answers are split, the model is unsure
- The approach is simple and cost-effective compared to fine-tuning
""",

    "2304.11477_LLM_P.txt": """
LLM+P: Empowering Large Language Models with Optimal Planning Proficiency
Authors: Bo Liu, Yuqian Jiang, Xiaohan Zhang, Qiang Liu, Shiqi Zhang, Joydeep Biswas, Peter Stone
Published: CoRL 2023

Abstract:
Large language models have demonstrated remarkable zero-shot generalization abilities across a variety of domains. However, their proficiency in planning is still limited compared to specialized planners. In this paper, we introduce LLM+P, a framework that combines the strengths of LLMs and classical planners. LLM+P takes a natural language problem description, converts it into a formal planning domain definition, and then uses a classical planner to find the optimal solution.

Core Method:
LLM+P is a framework that augments large language models with classical planning capabilities. It addresses the limitation that LLMs often produce suboptimal or invalid plans for complex planning problems.

The LLM+P Pipeline:
1. Natural Language Input:
   - User provides a planning problem in natural language
   - Includes initial state, goal state, and available actions
   - Example: "There are three blocks A, B, C. A is on B, B is on C. Move A to C."

2. Translation to PDDL:
   - The LLM translates the natural language description into PDDL (Planning Domain Definition Language)
   - Generates both the domain file (actions, predicates) and problem file (initial state, goal)
   - This is the key step - formalizing the problem for a planner

3. Classical Planning:
   - A PDDL planner (e.g., Fast Downward) takes the formal definition
   - Finds an optimal or valid plan
   - The planner guarantees correctness and optimality
   - This step is deterministic and reliable

4. Translation Back to Natural Language:
   - The plan is translated back into natural language
   - The LLM explains the solution in human-readable form
   - Provides step-by-step instructions

Key Features:
- Combines LLM language understanding with planner optimality
- Leverages decades of research in classical planning
- Guarantees correct and optimal plans
- Handles complex planning problems that LLMs struggle with
- The LLM serves as a translator, not a planner

Why LLM+P is Better than LLM-only:
- LLMs often hallucinate invalid actions or states
- LLMs may produce plans that don't achieve the goal
- LLMs don't guarantee optimality
- Classical planners provide formal guarantees
- The combination is more reliable than either alone

Experiments:
LLM+P was evaluated on planning benchmarks:
- Blocksworld: LLM+P achieved 96% success vs 58% for LLM-only
- Logistics: LLM+P achieved 88% success vs 42% for LLM-only
- Depot: LLM+P achieved 82% success vs 38% for LLM-only
- The plans from LLM+P were optimal or near-optimal
- LLM-only often produced invalid or suboptimal plans

Key Findings:
- LLMs are good at understanding natural language but bad at planning
- Classical planners are good at planning but require formal input
- Combining them gives the best of both worlds
- The translation step is critical and works well with current LLMs
- LLM+P demonstrates the value of integrating symbolic AI with neural methods
- The approach can be extended to other formal reasoning domains
""",

    "2209.07753_Code_as_Policies.txt": """
Code as Policies: Language Model Programs for Embodied Control
Authors: Jacky Liang, Wenlong Huang, Fei Xia, Peng Xu, Karol Hausman, Brian Ichter, Pete Florence, Andy Zeng
Published: ICRA 2023

Abstract:
Large language models have demonstrated the ability to generate code, but can this code be used to control robots? In this paper, we present Code as Policies (CaP), a framework that uses language models to generate code that controls robots. CaP extends the idea of chain-of-thought reasoning to robot control, allowing the model to generate executable code that interfaces with robot perception and action APIs.

Core Method:
Code as Policies is a framework that uses LLMs to generate robot control programs in Python. The key insight is that code provides a more expressive and precise representation for robot policies than natural language.

The CaP Framework:
1. Natural Language Instruction:
   - User gives a task in natural language
   - Example: "Stack the red block on the blue block"

2. LLM Generates Code:
   - The LLM generates Python code that solves the task
   - Code uses provided perception and action APIs
   - The code can include logic, loops, conditionals
   - Hierarchical code generation: first generate high-level functions, then fill in details

3. Perception APIs:
   - Functions for detecting objects, getting positions
   - Example: detect_objects(), get_position("red block")
   - The LLM calls these to understand the environment

4. Action APIs:
   - Functions for robot movement and manipulation
   - Example: move_to(position), pick(object), place(location)
   - The generated code calls these to execute actions

5. Execution:
   - The generated code is executed on the robot
   - Perception results feed back into the code
   - The robot performs the task autonomously

Key Features:
- Code is more expressive than natural language for policies
- Supports complex logic: conditionals, loops, arithmetic
- Hierarchical generation for complex tasks
- Can generalize to new tasks by composing API calls
- The LLM doesn't need robot-specific training

Why Code is Better than Natural Language for Policies:
- Code has precise syntax and semantics
- Code can express complex algorithms
- Code is executable and verifiable
- Code can use variables and state
- Code supports composition and abstraction

Experiments:
CaP was evaluated on robot manipulation tasks:
- Successfully completed complex stacking and sorting tasks
- Outperformed natural language policy baselines
- Generalized to novel object configurations
- Handled conditional tasks (e.g., "if red block exists, stack it")
- Demonstrated arithmetic and spatial reasoning in code
- The hierarchical approach improved success on long-horizon tasks

Key Findings:
- Code generation is an effective interface for robot control
- LLMs can generate meaningful robot programs with appropriate APIs
- The approach enables zero-shot generalization to new tasks
- Code provides better precision than natural language commands
- Hierarchical code generation handles longer tasks
- CaP demonstrates the potential of LLM-generated code for embodied AI
""",

    "2303.16434_TaskMatrix.txt": """
TaskMatrix.AI: Completing Tasks by Connecting Foundation Models with Millions of APIs
Authors: Yaobo Liang, Lei Ji, Chenfei Wu, Wenshan Wu, Lu Yuan, Yiwu Dai, Yang Ou, Shaoguang Mao, Yunong Jiao, Zehui Lin, et al.
Published: 2023

Abstract:
Artificial Intelligence has been dominated by foundation models in recent years. However, foundation models alone cannot complete many tasks that require interaction with digital devices or services. In this paper, we propose TaskMatrix.AI, a new AI ecosystem that connects foundation models with millions of existing models and APIs to complete various tasks.

Core Method:
TaskMatrix.AI is a framework that connects foundation models with existing APIs and services to accomplish complex tasks. It positions the foundation model as a central controller that can invoke specialized tools.

Architecture:
TaskMatrix.AI consists of four key components:

1. Multimodal Conversational Foundation Model (MCFM):
   - The central controller that understands user intent
   - Supports text, image, audio, and video inputs
   - Generates plans and selects appropriate APIs
   - Communicates with users in natural language

2. API Platform:
   - A repository of millions of existing APIs and models
   - Each API has a natural language description
   - APIs are categorized by domain and functionality
   - Includes both cloud services and local models
   - Examples: Office APIs, image generation, speech recognition, search

3. API Selector:
   - Matches task requirements to available APIs
   - Uses semantic search over API descriptions
   - Selects the most appropriate APIs for each subtask
   - Can combine multiple APIs for complex tasks

4. Action Executor:
   - Executes selected APIs with correct parameters
   - Handles API responses and errors
   - Passes results between APIs in multi-step tasks
   - Reports progress and final results to the user

The Task Execution Flow:
1. User provides a task in natural language (with optional media)
2. MCFM understands the task and decomposes it into subtasks
3. API Selector finds appropriate APIs for each subtask
4. Action Executor calls APIs in the correct order
5. Results are collected and integrated
6. MCFM generates a natural language response

Key Features:
- Connects foundation models to real-world services
- Leverages millions of existing APIs without retraining
- Supports multimodal inputs and outputs
- Can handle complex, multi-step tasks
- The API platform is extensible - new APIs can be added easily

Task Domains:
- Office automation: Word, Excel, PowerPoint manipulation
- Multimedia creation: image, audio, video generation and editing
- Information retrieval: search, question answering, data lookup
- E-commerce: product search, price comparison, ordering
- Smart home: device control, automation routines
- Software development: code generation, testing, deployment

Key Findings:
- Foundation models can effectively orchestrate existing APIs
- Natural language API descriptions enable zero-shot selection
- The ecosystem approach avoids reinventing existing capabilities
- TaskMatrix.AI demonstrates a path toward general-purpose AI assistants
- The framework can be extended to new domains by adding APIs
""",

    "2308.09687_Graph_of_Thoughts.txt": """
Graph of Thoughts: Solving Elaborate Problems with Large Language Models
Authors: Maciej Besta, Nils Blach, Ales Kubicek, Robert Gerstenberger, Lukas Gianinazzi, Joanna Gajda, Tomasz Lehmann, Hubert Niewiadomski, Piotr Nyczyk, Torsten Hoefler
Published: AAAI 2024

Abstract:
We introduce Graph of Thoughts (GoT), a framework that advances prompting capabilities in large language models beyond those offered by Chain-of-Thought or Tree of Thoughts. GoT enables modeling of information as an arbitrary graph, which provides several advantages: thoughts can be combined, decomposed, and refined, leading to more powerful and flexible reasoning.

Core Method:
Graph of Thoughts (GoT) is a prompting framework that represents reasoning as a graph structure, generalizing both Chain-of-Thought (linear) and Tree of Thoughts (hierarchical).

Key Concepts:
1. Thoughts as Graph Nodes:
   - Each thought is a node in a graph
   - Thoughts can be partial solutions, ideas, or reasoning steps
   - Nodes can have arbitrary connections to other nodes

2. Graph Operations:
   - Aggregation: combine multiple thoughts into one
   - Refinement: improve an existing thought
   - Generation: create new thoughts from existing ones
   - Decomposition: break a thought into sub-thoughts

3. Scoring and Ranking:
   - Each thought can be scored by the LLM
   - Scores guide which thoughts to explore further
   - The best thoughts are selected for output

4. Graph Structure Advantages:
   - Unlike trees, graphs allow cycles and merging
   - Multiple reasoning paths can converge
   - Ideas from different branches can be combined
   - This mirrors how humans actually think - combining ideas

The GoT Framework:
- Problem decomposition into thought units
- Graph construction through LLM operations
- Scoring and validation of thoughts
- Extraction of the best solution(s)

Comparison to Other Methods:
- Chain-of-Thought: linear, single path
- Tree of Thoughts: hierarchical, branches but no merging
- Graph of Thoughts: arbitrary graph, supports merging and cycles

Why GoT is More Powerful:
- Can combine insights from multiple reasoning paths
- Supports iterative refinement of ideas
- Enables more complex problem decomposition
- Better handles tasks with interdependent subtasks
- More flexible representation of thought processes

Experiments:
GoT was evaluated on various tasks:
- Sorting: Achieved 70% improvement over ToT in correctness
- Keyword counting: More accurate and consistent results
- Set intersection: Better handling of complex set operations
- Document merging: Produced higher quality merged documents
- The graph structure enabled combining partial solutions effectively

Key Findings:
- Graph structure provides significant advantages over tree structure
- Aggregation of thoughts improves solution quality
- The framework is general and applicable to many task types
- GoT demonstrates that more complex reasoning structures help LLMs
- The approach can be seen as extending search over reasoning spaces
- GoT opens new possibilities for LLM reasoning architectures
""",

    "2207.05608_Inner_Monologue.txt": """
Inner Monologue: Embodied Reasoning through Planning with Language Models
Authors: Fei Xia, Ted Xiao, Harris Chan, Jacky Liang, Pete Florence, Andy Zeng, Jonathan Tompson, Igor Mordatch, Yevgen Chebotar, Pierre Sermanet, et al.
Published: CoRL 2022

Abstract:
Recent works have shown that large language models can encode a broad range of semantic and commonsense knowledge that may be useful for language-guided robots. However, it remains unclear how to best leverage these models for robot control, especially in environments that require grounding language in physical observations and actions. In this paper, we propose Inner Monologue, a framework that uses language models for embodied reasoning by maintaining an internal monologue of thoughts.

Core Method:
Inner Monologue is a framework for robot control that uses LLMs to maintain a running internal monologue, enabling the robot to reason about its progress, handle failures, and adapt to new situations.

The Inner Monologue Framework:
1. Task Instruction:
   - User provides a high-level goal in natural language
   - Example: "Put the apple in the drawer"

2. Language Model Planning:
   - The LLM generates a plan or sequence of actions
   - Uses its commonsense knowledge to determine appropriate steps
   - The plan is expressed in natural language

3. Environment Feedback:
   - The robot executes actions and receives observations
   - Success/failure signals from the environment
   - Perception results (object detected, grasp successful, etc.)

4. Internal Monologue:
   - The LLM maintains a running commentary of thoughts
   - Reasons about whether actions succeeded
   - Adjusts plans based on feedback
   - Asks itself questions like "Did I pick up the apple?"
   - The monologue is fed back into the LLM for subsequent decisions

5. Adaptive Execution:
   - If an action fails, the LLM proposes alternatives
   - If the environment changes, the plan is updated
   - The robot continues until the goal is achieved

Key Features:
- Closed-loop reasoning with environment feedback
- Natural language as the reasoning medium
- Handles failures and unexpected situations
- No fine-tuning required - uses pretrained LLMs
- The internal monologue makes reasoning interpretable

Why Inner Monologue Works:
- Language models have rich commonsense knowledge
- The monologue provides context for decision making
- Feedback from the environment grounds the reasoning
- The approach is more robust than open-loop planning
- Natural language enables flexible error recovery

Experiments:
Inner Monologue was evaluated on robot manipulation tasks:
- Successfully completed long-horizon tasks with multiple steps
- Recovered from failures (dropped objects, blocked paths)
- Adapted to changing environments
- Outperformed baselines that didn't use language feedback
- The internal monologue improved task success rate by 30%+
- Human evaluators found the reasoning process interpretable

Key Findings:
- LLMs can effectively reason about robot tasks with feedback
- Internal monologue enables adaptive behavior
- The approach handles real-world uncertainty better
- Language provides a flexible medium for robot reasoning
- Inner Monologue demonstrates the value of closed-loop LLM control
- The framework can be applied to various robot platforms
""",

    "2401.03568_Hallucination_Survey.txt": """
A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions
Authors: Lei Huang, Weiang Shi, Yufei Wang, Guanting Dong, Fengyu Cai, Yuxuan Wang, Enhong Chen, Zhenguo Li, Shuang Li
Published: 2024

Abstract:
Large language models have demonstrated remarkable capabilities in various natural language processing tasks. However, they are prone to hallucinations, generating content that is fabricated or inconsistent with factual information. This survey provides a comprehensive review of hallucination in LLMs, covering definitions, taxonomies, detection methods, and mitigation strategies.

Core Content:
Definition of Hallucination:
Hallucination in LLMs refers to generated content that is:
- Factually incorrect or unsupported by the input
- Inconsistent with established knowledge
- Fabricated or made-up information
- Presented with high confidence despite being wrong

Taxonomy of Hallucinations:

1. Factuality Hallucination:
   - Factual inconsistency with world knowledge
   - Example: stating incorrect historical dates
   - Subtypes: entity errors, relation errors, attribute errors

2. Faithfulness Hallucination:
   - Inconsistency with the provided source/input
   - Example: summarization that adds information not in the text
   - Subtypes: unsupported claims, contradictory statements

3. Intentional vs. Unintentional:
   - Intentional: model knowingly generates false information
   - Unintentional: model believes the information is correct

Causes of Hallucination:

1. Data-Related Causes:
   - Training data contains errors or biases
   - Knowledge cutoff - model lacks recent information
   - Data duplication and memorization issues
   - Imbalanced data representation

2. Model-Related Causes:
   - Parametric knowledge limitations
   - Attention mechanism imperfections
   - Decoding strategies that favor fluency over accuracy
   - Overconfidence in predictions

3. Training-Related Causes:
   - Alignment between training objectives and factual accuracy
   - Reinforcement learning from human feedback (RLHF) side effects
   - Inadequate penalization of false statements

Detection Methods:
1. Fact-checking based: verify claims against knowledge bases
2. Model-based: use another LLM to detect hallucinations
3. Self-consistency: check if multiple generations agree
4. Entailment-based: verify if output is entailed by input
5. Uncertainty estimation: detect when model is uncertain

Mitigation Strategies:
1. Training-time:
   - Improved data curation and filtering
   - Knowledge augmentation during training
   - Contrastive learning to reduce hallucination
   - Better alignment objectives

2. Inference-time:
   - Retrieval-augmented generation (RAG)
   - Chain-of-thought verification
   - Self-consistency and majority voting
   - Temperature adjustment and constrained decoding

3. Post-hoc:
   - Fact-checking and correction
   - Output filtering and editing
   - Uncertainty calibration

Evaluation Benchmarks:
- TruthfulQA: measures truthfulness in questions
- HalluEval: evaluates hallucination in dialogue
- FactScore: assesses factual precision in long text
- FEVER: fact verification benchmark
- Various domain-specific benchmarks

Open Challenges:
- Defining and measuring hallucination consistently
- Balancing creativity and factuality
- Handling hallucination in multi-turn conversations
- Real-time hallucination detection
- Cross-lingual hallucination
- Hallucination in multimodal models

Key Findings:
- Hallucination remains a fundamental challenge for LLMs
- RAG is one of the most effective mitigation strategies
- No single method completely eliminates hallucination
- Detection is as important as prevention
- The field needs better evaluation standards
- Hallucination management requires a holistic approach
""",
}


def main():
    print(f"创建 {len(PAPERS)} 篇论文的文本测试集...")
    for filename, content in PAPERS.items():
        filepath = SAVE_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"  ✓ {filename} ({len(content)} chars)")

    print(f"\n完成！共 {len(PAPERS)} 篇论文文本")
    print(f"目录: {SAVE_DIR}")


if __name__ == "__main__":
    main()
