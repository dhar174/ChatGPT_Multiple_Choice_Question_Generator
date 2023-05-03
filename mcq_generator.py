import regex as re
from asyncore import loop
import random
import signal
import sys
import time
import tkinter

import numpy
import openai
import os

# Set your API key
openai.api_key = "your-api-key-here"
display_mode = False
# Number of questions to generate
subject = "broad subject here"

num_questions = 35
# Domains and sub-objectives (example)
domains = ["domains within subject here"]
sub_objectives = ["sub-objectives within domain here"]


# Bloom's taxonomy level and difficulty
bloom_level = "Analyze or above"
difficulty = "Easy, Intermediate, or Advanced"

textbook_excerpts = {
    "Textbook excerpt 1": f"Textbook excerpt 1 here",
    "Textbook excerpt 2": f"Textbook excerpt 2 here",
    "Textbook excerpt 3": f"Textbook excerpt 3 here",

}
requirements = [
    f"Write original questions in passive voice and include a 1-3 sentence general explanation (GE) for each answer choice without revealing correct answers in GEs for incorrect options. Focus on comparing and contrasting {sub_objectives} in the context of {subject}. Make sure the questions match the knowledge level of a {subject} student and align with the domain, as well as one or more of the following sub-objectives: {sub_objectives}. The questions must be technically accurate. All terms in the question must be defined in the textbook. The question must be based on the textbook excerpts that will be provided. The question must have four answer options. The question must have a GE for each answer option. Very importantly, the question must be unique and unplagiarized. Any level of plagiarism is unacceptable, so make each questions unique. Lastly, each answer option must be no more than a few words.",]

# Textbook excerpts


def signal_handler(signal, frame):
    loop.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def slice_string(text, n, from_start=True):
    words = text.split()
    if from_start:
        return ' '.join(words[:n])
    else:
        return ' '.join(words[-n:])

def prompt_gpt(messages, model="gpt-3.5-turbo"):
    if model != "text-davinci-003" and model != "curie" and model != "babbage":
        response = None
        # print("messages:", messages)
        try:
            time.sleep(1)
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
            )
            time.sleep(1)
        except Exception as e1:
            try:
                time.sleep(10)
               
               
                messages = list(messages)
                messages.pop(1)
       
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                )
                time.sleep(1)
            except Exception as e2:
                print("len of list(messages):", len(list(messages)))
                print("response:", response)
                print("e1:", e1)
                print("e2:", e2)
                return "I'm sorry, I don't know."
        # print("GPT-3 response:", response)
    else:
        try:
            time.sleep(1)
            response = openai.Completion.create(
                engine=model,
                prompt=messages,
            )
            time.sleep(10)
        except:
            try:
                time.sleep(30)
                list(messages).remove(list(messages)[-1])
                response = openai.Completion.create(
                    engine=model,
                    prompt=messages,
                )
                time.sleep(1)
            except:
                print("list(messages):", list(messages))
                print("response:", response)
                return response
        # print("GPT-3 response:", response)
        for choice in response['choices']:
            print(f"Response choice from {model}: ", choice['text'])
            if "yes" in choice['text'] or "no" in choice['text']:
                return choice['text']
            else:
                return response['choices'][0]['text']
    return response['choices'][0]['message']['content']


domain = domains[0]


def display_text(text, seconds, fontsize=28):
    def close_window():
        root.destroy()

    root = tkinter.Tk()
    root.title("Text Display")

    # Set window dimensions
    window_width = 2200
    window_height = 900

    # Calculate screen center coordinates
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))

    # Set window geometry and position
    root.geometry(
        f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    label = tkinter.Label(root, text=text, font=("Roboto Mono", fontsize, "bold"), bg="lightblue", relief="groove",
                          borderwidth=4, wraplength=window_width - 100, justify="center", anchor="center", padx=50, pady=50)
    label.pack(expand=True, fill="both")

    root.after(int(seconds * 1000), close_window)
    root.mainloop()


unique_questions = set()


def check_unique(question, messages):
    # Check if the question is unique
        if question not in unique_questions:

                is_unique = True
                return is_unique
        else:
            # Remove the non-unique question from the messages list and try again
            messages.pop()
            messages.pop()
            return False

def check_plagiarism(questions):
    subs_string = ""
    for sub_objective in sub_objectives:
        subs_string += sub_objective + ", "

    messages_check = [{"role": "system", "content": f"You are a helpful professional question reviewer that only answers yes or no at all times. You are knowledgeable in {subject}, and your function is to judge whether a question is consistent with the {requirements[0]}, that all answer options are present in the textbook excerpts that will be provided below and that the question as a whole aligns with the textbook excerpts, and also aligns with the domain {domain} and addresses in some way at least one of the subobjectives in {subs_string}. You will ONLY respond with either a YES or a NO to indicate your judgement regarding whether the question meets the given requirements. You must reject any questions that are off topic, and you must also reject any questions that are too vague or that have an answer or answer options that are subjective or not firmly confirmable.", }]
    for excerpt in textbook_excerpts.values():
        messages_check.append(
            {"role": "user", "content": f"Here is the textbook text excerpt the question and options must be based on: {excerpt}"})
    messages_check.append(
        {"role": "user", "content": f"Check for consistency with the provided text and other requirements {requirements}. If the question does not meet the requirements, please ONLY respond with a yes or a no"})
    print("Question Checker is beginning checking...\n")
    if (display_mode):
        display_text("Question Checker is beginning checking... \n", 3)
    # msg_list = []

    q_checks = [False, False, False]
    check_responses = ["", "", ""]

    # for message in messages_check:
    #     msg_list.append(message["content"])
    #     print(message["content"])
    for x in range(0, 2):
        lbl = ""
        plagiarisim_checker_prompt = f"Please judge whether or not you think this is text is directly plagiarized from another work or IP of any kind, giving a 'yes' answer if you believe it is not plagiarized (yes meaning the question is usable) and a 'no' (as in dont use the question) answer if it is not plagiarized. This is the first question in the set, so please just make a yes or no judgement on whether this is plagiarized or not. Here is the current question to consider: {questions[x]}"

        final_clean = False
        revised_clean = False
        original_clean = False
        if (x == 0):
            lbl = "Final Question"
            if (display_mode):
                display_text("Checking Final Question... \n", 3)

            unique_verdict = prompt_gpt(
                plagiarisim_checker_prompt, "text-davinci-003")
            if ("yes" in unique_verdict.lower() or ("unique" in unique_verdict.lower() and "not " not in unique_verdict.lower() and "no " not in unique_verdict.lower())):
                    print("Question is not plagiarized, probably.\n")
                    q_checks[x] = True
                    if (display_mode):
                        display_text(
                            "Question is not plagiarized, probably.", 2)
                    final_clean = True
            elif ("no " in unique_verdict.lower() or "not " in unique_verdict.lower()):
                print("Question may be plagiarized. Not usable. \n")
                if (display_mode):
                    display_text(
                        "Question may be plagiarized. Not usable.", 10)
            messages_check.append(
                {"role": "user", "content": questions[x]})

        elif (x == 1):
            lbl = "Revised Question"
            if (display_mode):
                display_text("Checking Revised Question... \n", 3)
            unique_verdict = prompt_gpt(
                plagiarisim_checker_prompt, "text-davinci-003")
            if ("yes" in unique_verdict.lower() or ("unique" in unique_verdict.lower() and "not " not in unique_verdict.lower() and "no " not in unique_verdict.lower())):
                print("Question is not plagiarized, probably.\n")
                q_checks[x] = True
                if (display_mode):
                    display_text(
                        "Question is not plagiarized, probably.", 2)
                    revised_clean = True
            elif ("no " in unique_verdict.lower() or "not " in unique_verdict.lower()):
                print("Question may be plagiarized. Not usable. \n")
                if (display_mode):
                    display_text(
                        "Question may be plagiarized. Not usable.", 10)
            messages_check.append(
                {"role": "user", "content": questions[x]})
            
        elif (x == 2):
            lbl = "Original Question"
            if (display_mode):
                display_text("Checking Original Question... \n", 3)
            messages_check.append({"role": "user", "content": questions[x]})
            unique_verdict = prompt_gpt(
            plagiarisim_checker_prompt, "text-davinci-003")
            if ("yes" in unique_verdict.lower() or ("unique" in unique_verdict.lower() and "not " not in unique_verdict.lower() and "no " not in unique_verdict.lower())):
                    print("Question is not plagiarized, probably.\n")
                    q_checks[x] = True
                    if (display_mode):
                        display_text(
                            "Question is not plagiarized, probably.", 2)
                    original_clean = True
            elif ("no " in unique_verdict.lower() or "not " in unique_verdict.lower()):
                print("Question may be plagiarized. Not usable. \n")
                if (display_mode):
                    display_text(
                        "Question may be plagiarized. Not usable.", 10)
                messages_check.append(
                    {"role": "user", "content": questions[x]})
        check_responses[x] = prompt_gpt(messages_check)
        print("Sleeping for 20 seconds...")
        clean_matrix = [final_clean, revised_clean, original_clean]
        time.sleep(20)
        print("Question Checker's response: for " +
                lbl + check_responses[x])
        if (display_mode):
            display_text("Question Checker's response: for " +
                            lbl + check_responses[x], 8)
        if ("yes" in check_responses[x].lower() and clean_matrix[x] == True):
            q_checks[x] = True
            if (display_mode):
                display_text(
                    f"Question Checker's response: for {lbl} " + check_responses[x], 8)
            if (display_mode):
                display_text("Question meets the requirements! \n", 3)
        elif ("no" in check_responses[x].lower() or clean_matrix[x] == False):
            q_checks[x] = False
            if (display_mode):
                display_text(
                    f"Question Checker's response: for {lbl} " + check_responses[x], 8)
            if (display_mode):
                display_text("Question does not meet the requirements! \n", 3)

        print("\n")
    return q_checks, check_responses
        


# Main loop for generating questions
def main():
    global requirements
    global textbook_excerpts
    global sub_objectives
    global bloom_level
    global difficulty
    global subject
    global domain
    global num_questions
    global subject
    print("Welcome to the question generator!")
    print("This program will generate questions based on the following requirements:")
    print(requirements)
    print("The program will generate questions based on the following textbook excerpts:")
    print(textbook_excerpts)
    print("The program will generate questions based on the following sub-objectives:")
    print(sub_objectives)
    print("The program will generate questions based on the following Bloom's taxonomy level:")
    print(bloom_level)
    print("The program will generate questions based on the following difficulty:")
    print(difficulty)
    print("The program will generate questions based on the following subject:")
    print(subject)
    print("The program will generate questions based on the following domain:")
    print(domain)
    print("The program will generate the following number of questions:")
    print(num_questions)

    i = 0
    while i < num_questions:
        excerpts_list = [textbook_excerpts.values()]
        # Step 1: Establish a list of messages for question writing
        messages_rewrite_pass = False
        
        messages_write = [
            {
                "role": "system",
                "content": f"You are a helpful assistant that creates multiple choice questions. You are working with a {subject} professor to create questions for the {domain} domain."
                        f"Follow the rules and requirements, which are {requirements} to create a question that aligns with the domain '{domain}' within the topic '{subject}'"
                        f"and the sub-objectives '{sub_objectives[i % len(sub_objectives)]}'."
                        f"Your question should be at the Bloom's taxonomy level '{bloom_level}' and the difficulty '{difficulty}'."
                        f"Your question should also include a scenario."
                        f"Your question should be based on the following textbook excerpts, and all answer options must be based on the excerpts: {excerpts_list[i % len(excerpts_list)]}."
                        f"Your question should have four answer options."
                        f"Your question should have a General Explanation for each answer option."
                        f"Create a multiple choice question about {domain} based on the text. Each question should have 4 answer options with one or more correct answers. Write questions in passive voice and include a 1-3 sentence explanation for each answer choice without revealing correct answers in incorrect options. Focus on comparing and contrasting the following sub-objectives: {sub_objectives[i % len(sub_objectives)]} in the context of {subject}. Make sure the questions match the knowledge level of a {subject} student and align with the domain and one or more of the following sub-objectives: {sub_objectives[i % len(sub_objectives)]}."

            },
            {
                "role": "user",
                "content": "PLACE YOUR QUESTION EXAMPLE HERE"
            },
            {
                "role": "user",
                "content": "PLACE YOUR QUESTION EXAMPLE HERE"
            },
            # Include example questions here, if desired
        ]

        # Step 2: Prompt the question writer to write a question
        messages_write.append(
            {"role": "user", "content": "Write a multiple choice question following the requirements based on the provided excerpts."})
        print("Question Writer is beginning writing...\n")
        if(display_mode):
            display_text("Question Writer is beginning writing...", 3)
        question = prompt_gpt(messages_write)
        print("Question Rough Draft: \n", question)
        if(display_mode):
            display_text(f"Question Rough Draft: + {question}\n", 10,11)
           
        print("\n")
        print("Sleeping for 20 seconds...")
        if (display_mode):
            display_text("Sleeping for 20 seconds...", 3)
        time.sleep(20)
        # Step 3: Revise and edit the question for accuracy and alignment
        
        messages_revise = [
            {
                "role": "system",
                "content": f"You are a helpful assistant that revises and edits multiple choice questions for accuracy and alignment with the provided text. You only answer all inputs with a simple yes or no, and you never say any more. This is an important rule, and punishment will be dealt if it is not adhered to. The revised question should be align not only with the original question as much as possible, but also {domain} and the sub-objectives {sub_objectives[i % len(sub_objectives)]}. You are working with a {subject} professor to create questions for the {domain} domain."
                        f"Follow the rules and requirements, which are {requirements} to create a question that aligns with the domain '{domain}' within the topic '{subject}'"
                        f"and the sub-objectives '{sub_objectives[i % len(sub_objectives)]}'."
                        f"Your question should be at the Bloom's taxonomy level '{bloom_level}' and the difficulty '{difficulty}'."
                        f"Your question should also include a scenario."
                        f"Your question should be based on the following textbook excerpts, and all answer options must be based on the excerpts: {excerpts_list[i % len(excerpts_list)]}."
                        f"Your question should have four answer options."
                        f"Your question should have a General Explanation for each answer option."
                        f"Create a multiple choice question about {domain} based on the text. Each question should have 4 answer options with one or more correct answers. Write questions in passive voice and include a 1-3 sentence explanation for each answer choice without revealing correct answers in incorrect options. Focus on comparing and contrasting the following sub-objectives: {sub_objectives[i % len(sub_objectives)]} in the context of {subject}. Make sure the questions match the knowledge level of a {subject} student and align with the domain and one or more of the following sub-objectives: {sub_objectives[i % len(sub_objectives)]}."
            },
            {"role": "user", "content": f"Original question: {question}"},]
        for excerpt in textbook_excerpts.values():
            messages_revise.append(
                {"role": "user", "content": f"Text: {excerpt}"})
        messages_revise.append(
            {"role": "user", "content": "Revise the question for accuracy and alignment with the text."})
        print("Question Reviser is beginning revision...\n")
        if(display_mode):
            display_text("Question Reviser is beginning revision...",3)
        revised_question = prompt_gpt(messages_revise)
        print("Question Revised: ", revised_question)
        if(display_mode):
            display_text("Question revised! "+ revised_question,10,11)
        print("\n")
        print("Sleeping for 20 seconds...")
        if (display_mode):
            display_text("Sleeping for 20 seconds...", 3)
        time.sleep(20)
        # Step 4: Rewrite the question for Bloom's taxonomy level, difficulty, and scenario
        
        while not messages_rewrite_pass:
            messages_rewrite = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that rewrites multiple choice questions to meet specific Bloom's taxonomy levels, difficulties, and scenarios."
                },
                {"role": "user", "content": f"Revised question: {revised_question}"},
            ]
            messages_rewrite.append({"role": "user", "content": f"Rewrite the question stem of a multiple choice question to meet the Bloom's taxonomy level '{bloom_level}', the difficulty '{difficulty}', and include a scenario. Leave all answer options the same, and leave the General Explanations the same. Preserve the original question as much as possible. Include the whole question, including the original question stems and answer options, in the rewritten question."})
            print("Question Rewriter is beginning rewriting...\n")
            if(display_mode):
                display_text("Question Rewriter is beginning rewriting...",3)
            
            final_question = prompt_gpt(messages_rewrite)
            print("Question Final Draft: ", final_question)
            if(display_mode):
                display_text("Question Final Draft: "+ final_question,10,11)
            print("\n")
            if (check_unique(final_question, messages_rewrite)):
                time.sleep(1)
                sorted_questions = sorted(list(unique_questions), key=len)
                sorted_questions = numpy.array(sorted_questions)
                if(len(sorted_questions) > 0):
                    plagiarisim_checker_prompt = f"Check that the following question is unique and different from the previous questions. It should not be asking the same thing as any of the previous questions. Respond with 'yes' if it is unique (yes meaning the question is usable), and 'no' (as in dont use the question) if it is not. Please also judge whether or not you think this is text is directly plagiarized from a previous work, giving a 'yes' answer if you believe it is not plagiarized (and thus can be used) and a no answer if it is plagiarized (no, as in dont use the question). These are the previous questions: {sorted_questions[ i % len(sorted_questions)]}  and here is the current question to consider: {final_question}"
                else:
                    print("No previous questions to compare to.\n")
                    plagiarisim_checker_prompt = f"Please judge whether or not you think this is text is directly plagiarized from a previous work, giving a 'yes' answer if you believe it is not plagiarized (yes meaning the question is usable) and a 'no' (as in dont use the question) answer if it is not plagiarized. This is the first question in the set, so please just make a yes or no judgement on whether this is plagiarized or not. Here is the current question to consider: {final_question}"

                
                unique_verdict = prompt_gpt(
                    plagiarisim_checker_prompt, "text-davinci-003")
                if ("yes" in unique_verdict.lower() or ("unique" in unique_verdict.lower() and "not " not in unique_verdict.lower() and "no " not in unique_verdict.lower())):
                    print("Question is unique.\n")
                    unique_questions.add(question)
                    if (display_mode):
                        display_text("Question is unique.", 2)
                    messages_rewrite_pass = True
                elif ("no " in unique_verdict.lower() or "not " in unique_verdict.lower()):
                    print("Question may not be not unique.\n")
                    if (display_mode):
                        display_text(
                            "Question may not be unique. Making another attempt.", 3)
                
                    messages_rewrite_pass = False
            print("Sleeping for 20 seconds...")
            if (display_mode):
                display_text("Sleeping for 20 seconds...", 3)
            time.sleep(20)
        
        # Step 5: Check the question for plagiarism

        q_checks, check_responses = check_plagiarism(
            [final_question, revised_question, question,]),

        # Step 6: Save the question to a file
        rand = random.randint(0, 100)
        # create a random character to append to the question
        rand_char = chr(rand)
        # safetext = re.sub(r'[^\w\s]', '', rand_char)
        rand_char = re.sub(r"[^ .a-zA-Z0-9\']+", "", rand_char)
        os.makedirs(domain, exist_ok=True)
        domain_folder = domain
        if (q_checks[0] == True):
            with open(f"{domain_folder}/question_{i+1}_{rand_char}_final_{domain}.txt", "w") as f:
                f.write(final_question)
                f.write("\n")
                f.write("\n")
                # f.write("General Explanations: \n")
                f.write("\n")
                f.write("\n")
                f.write(
                    "Question Checker's response for Final Question \n" + check_responses[0])
                # f.write(explanations)
            print("Final Question saved to file.\n")
            if(display_mode):
                display_text("Final Question saved to file.",3)
        if(q_checks[1] == True):
            with open(f"{domain_folder}/question_{i+1}_{rand_char}_original_{domain}.txt", "w") as f:
                f.write(question)
                f.write("\n")
                f.write("\n")
                # f.write("General Explanations: \n")
                # f.write(explanations)
                f.write("\n")
                f.write("\n")
                f.write(
                    "Question Checker's responsefor Original Question  \n" + check_responses[1])
                print("Original Question saved to file.\n")
                if(display_mode):
                    display_text("Original Question saved to file.",3)
                
        if (q_checks[2] == True):
            with open(f"{domain_folder}/question_{i+1}_{rand_char}_revised_{domain}.txt", "w") as f:
                f.write(revised_question)
                f.write("\n")
                f.write("\n")
                # f.write("General Explanations: \n")
                f.write("\n")
                f.write("\n")
                f.write(
                    "Question Checker's response for for Revised Question \n" + check_responses[2])
                # f.write(explanations)
            print("Revised Question saved to file.\n")
            if(display_mode):
                display_text("Revised Question saved to file.",3)
        yes_count = 0
        for _check in q_checks:
            if (_check == True):
                yes_count += 1
        if (yes_count < 1):
            print("No Questions meet the requirements. Making another attempt.\n")
            if(display_mode):
                display_text("Final Question does not meet the requirements. Making another attempt.",3)
            i-=1
        i += 1
        print("Question number: ", i)
        if(display_mode):
            display_text("Question number: "+ str(i),3)
        print("\n")
        print("Sleeping for 20 seconds... \n")
        if(display_mode):
            display_text("Sleeping for 20 seconds... \n",3)
        time.sleep(20)


if __name__ == "__main__":
    main()
