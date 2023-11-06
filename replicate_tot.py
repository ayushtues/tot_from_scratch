import replicate
import os 



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


input_number = "5 10 12 11"
task_prompt = f"Your goal is to use the given numbers and the basic arithmetic operations (+, -, *, /) to obtain the number 24. You can use each number only once, but you can use the operations in any order and as many times as you want. This task will take multiple steps. For the current step, you choose two numbers and perform an arithmetic operation on them. \n\nExamples\nInput: 4 9 10 13\nPossible next steps:\nOutput1: 4 + 9 = 13 (left 10 13 13)\nOutput2: 10 - 4 = 6 (left: 6 9 13)\nOutput3: 10/9 = 1 (left: 4 1 13)\nOutput4: 9*13 = 117 (left: 4 10 117)\n\nInput: 4 10 12 1\nPossible next steps: \nOutput1: 12 - 10 = 2 (left: 4 2 1)\nOutput2: 4 * 10 = 40 (left: 40 12 1)\nOutput3: 12 + 1 = 13 (left: 4 10 13)\nOutput4 12/10 = 1 (left: 4 1 1)\n\nNow for the below input\nInput: {input_number}\nPossible next steps:"

output = replicate.run(
    "meta/llama-2-7b-chat:13c3cdee13ee059ab779f0291d29054dab00a47dad8261375654de5540165fb0",
    input={"prompt": task_prompt}
)
output_all = ""
for item in output:
    output_all += item

print(extract_proposals(output_all))