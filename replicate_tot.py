import replicate
from os.path import join, dirname
from dotenv import load_dotenv
from collections import defaultdict

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def run_replicate(prompt):
    output = replicate.run(
        "meta/llama-2-7b-chat:13c3cdee13ee059ab779f0291d29054dab00a47dad8261375654de5540165fb0",
        input={"prompt": prompt, "max_new_tokens": 500, "temperature": 0.55, "top_p1": 1.0, "repetition_penalty": 1.0, "system_prompt": ""}
    )
    output_all = ""
    for item in output:
        output_all += item
    return output_all

def extract_proposals(text):
    text = text.split("\n")

    text = [item for item in text if "Output" in item]

    proposals = []  
    for x in text:
        x = x.split("left:")
        if len(x) == 2 : 
            x = x[1][:-1]
            proposals.append(x)
    return proposals

def extract_evaluation(text):
    text  = text.lower()
    if "impossible" in text:
        return 0
    elif "sure" in text:
        return 1
    else:
        return 0.5

curr_states = ["5 10 12 11"]

TREE_DEPTH = 3
PROPOSAL_RUNS_PER_STATE = 2
EVAL_RUNS_PER_STATE = 3
BRANCH_FACTOR = 3

for _ in range(TREE_DEPTH):
    proposal_and_score = []
    for state in curr_states:
        proposal_prompt = f"Your goal is to use the given numbers and the basic arithmetic operations (+, -, *, /) to obtain the number 24. You can use each number only once, but you can use the operations in any order and as many times as you want. This task will take multiple steps. For the current step, you choose two numbers and perform an arithmetic operation on them. \n\nExamples\nInput: 4 9 10 13\nPossible next steps:\nOutput1: 4 + 9 = 13 (left 10 13 13)\nOutput2: 10 - 4 = 6 (left: 6 9 13)\nOutput3: 10/9 = 1 (left: 4 1 13)\nOutput4: 9*13 = 117 (left: 4 10 117)\n\nInput: 4 10 12 1\nPossible next steps: \nOutput1: 12 - 10 = 2 (left: 4 2 1)\nOutput2: 4 * 10 = 40 (left: 40 12 1)\nOutput3: 12 + 1 = 13 (left: 4 10 13)\nOutput4 12/10 = 1 (left: 4 1 1)\n\nNow for the below input\nInput: {state}\nPossible next steps:"

        proposals = []
        for _ in range(PROPOSAL_RUNS_PER_STATE):
            proposals += extract_proposals(run_replicate(proposal_prompt))
    
        for proposal in proposals:
            eval_prompt = "Evaluate if given numbers can reach 24 using basic arithmetic operations (+, -, *, /).You can use each number only once, but you can use the operations in any order and as many times as you want.\n\nSome examples are:\nInput: 10 14 -> 10 + 14 = 24. -> {Output: \"sure\"}\nInput: 4 9 10 13 -> (10- 4) * (13- 9) = 24. -> {Output: \"sure\"}\nInput: 20 10: Not possible -> {Output: \"impossible\"}\n\nCan the numbers" + proposal + "reach 24?"

            score = 0
            for _ in range(EVAL_RUNS_PER_STATE):
                score += extract_evaluation(run_replicate(eval_prompt))
            
            proposal_and_score.append((proposal, score/3))
    
    # sort proposals by score
    proposal_and_score.sort(key=lambda x: x[1], reverse=True)
    curr_states = [item[0] for item in proposal_and_score[:BRANCH_FACTOR]]

print(curr_states[0])
