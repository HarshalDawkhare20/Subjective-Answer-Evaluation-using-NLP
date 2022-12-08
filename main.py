import nltk
from rake_nltk import Rake
import json
from nltk.corpus import wordnet as wn
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
import streamlit as st
import ast

st.title("Subjective Paper Evaluation")

st.sidebar.subheader("About us")
st.sidebar.write("""
\nRahul Retharekar
\nHarshal Dawkhare
\nShreyash Bhatale""")

# Defining a function to convert Penn Treebank tag to a simplified Wordnet tag


def penn_to_wn(tag):
    if tag.startswith('N'):
        return 'n'

    if tag.startswith('V'):
        return 'v'

    if tag.startswith('J'):
        return 'a'

    if tag.startswith('R'):
        return 'r'
    return None


def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None

    try:
        return wn.synsets(word)[0]
    except:
        return None


def sentence_similarity(model_key, student_key):
    """ compute the sentence similarity using Wordnet """
    # Tokenize and tag
    lemmatizer = WordNetLemmatizer()

    model_answer_tokenized = word_tokenize(model_key)
    model_pos_tagged = pos_tag(model_answer_tokenized)
    model_tagged = [(lemmatizer.lemmatize(word[0].lower(), penn_to_wn(word[1])), word[1]) for word in model_pos_tagged]
    #     model_lemmatized = [lemmatizer.lemmatize(word[0].lower(),penn_to_wn(word[1])) for word in model_pos_tagged]
    #     model_tagged = pos_tag(model_lemmatized)
    #     print(model_tagged)
    #     model_tagged = pos_tag(model_answer_words)

    student_answer_tokenized = word_tokenize(student_key)
    student_pos_tagged = pos_tag(student_answer_tokenized)
    student_tagged = [(lemmatizer.lemmatize(word[0].lower(), penn_to_wn(word[1])), word[1]) for word in student_pos_tagged]
    #     student_lemmatized = [lemmatizer.lemmatize(word[0].lower(),penn_to_wn(word[1])) for word in student_pos_tagged]
    #     student_tagged = pos_tag(student_lemmatized)
    #     print(student_tagged)

    #     model_tagged = pos_tag(lemmatizer.lemmatize(word_tokenize(model_key)))
    #     student_tagged = pos_tag(lemmatizer.lemmatize(word_tokenize(student_key)))

    # Get the synsets for the tagged words
    model_syn = [tagged_to_synset(*tagged_word) for tagged_word in model_tagged]
    student_syn = [tagged_to_synset(*tagged_word) for tagged_word in student_tagged]

    # Filter out the Nones
    model_syn_filtered = [ss for ss in model_syn if ss]
    student_syn_filtered = [ss for ss in student_syn if ss]
    print(model_syn_filtered, student_syn_filtered)

    score, count = 0.0, 0

    for word in model_syn_filtered:
        # Get the similarity value of the most similar word in the other sentence
        #         scores = [word.path_similarity(ss) for ss in student_syn_filtered]
        scores = [word.wup_similarity(ss) for ss in student_syn_filtered]
        #         print(scores)
        scores = [s for s in scores if s]
        print(scores)
        if len(scores) != 0:
            best_score = max(scores)
            score += best_score
            count += 1

    # Average the values
    if count != 0:
        score /= count
        return score
    return 0


# answers1 = []
# f = open('answers1.txt')
# lines = f.readlines()

# for line in lines:
#     if line != '\n':
#         answers1 += [line.replace('\n', '')]
# # print(answers1)

# with open('model_answers.txt') as f:
#     data = f.read()

# print("Data type before reconstruction : ", type(data))

# # reconstructing the data as a dictionary
# model_answer_list = json.loads(data)

# print("Data type after reconstruction : ", type(model_answer_list))
# print(model_answer_list)

# model_answer = {'FCFS stands for First Come, First Served.': 0.5, 'It is a type of scheduling algorithm.': 0.5, 'In this scheme, if a process requests the CPU first, it is allocated to the CPU first.': 1, 'Its implementation is managed by a FIFO queue.': 1, 'It is simple and easy to understand & implement.': 1, 'The process with less execution time suffer i.e. waiting time is often quite long.': 1, 'This effect results in lower CPU and device utilization.': 1, 'FCFS algorithm is particularly troublesome for time-sharing systems, where it is important that each user get a share of the CPU at regular intervals.': 1}
# student_answer = 'FCFS means First Come First Served. It is an operating system scheduling algorithm that automatically executes queued requests and processes in order of their arrival. Advantages is that it is simple and easy to understand. Disadvantages is that the process with less execution time suffer that is waiting time is often quite long.'

# model_answer = json.loads(st.text_input("Model answer: "))
# mode
# l_answer="{'dummy':1}"
model_answer = st.text_area("Model answer: ", placeholder="Model answer goes here")
if len(model_answer):
    model_answer = ast.literal_eval(model_answer)
student_answer = st.text_area("Student answer: ", placeholder="Student answer goes here")
if len(model_answer) and len(student_answer):

    # print(model_answer)
    # print(student_answer)

    # r = Rake()
    # lemmatizer = WordNetLemmatizer()
    # r.extract_keywords_from_text(student_answer)
    # student_keywords = r.get_ranked_phrases()
    # print(student_keywords)
    # for sentence in model_answer.keys():
    #     r.extract_keywords_from_text(sentence)
    #     sentence_keywords = r.get_ranked_phrases()
    #     print(sentence_keywords)
    # error loop below
    # for sentence_keyword in sentence_keywords:
    #     for student_keyword in student_keywords:
    #         print(lemmatizer.lemmatize([x for x in word_tokenize(sentence_keyword)]))
    #         # print(sentence_keyword,",",student_keyword,",",sentence_similarity(sentence_keyword, student_keyword))
    #

    r = Rake()
    r.extract_keywords_from_text(student_answer)
    student_keywords = r.get_ranked_phrases()
    grand_total = 0
    for sentence in model_answer.keys():
        r.extract_keywords_from_text(sentence)
        sentence_keywords = r.get_ranked_phrases()
        total = 0
        for sentence_keyword in sentence_keywords:
            best = None
            max_score = 0
            for student_keyword in student_keywords:
                if sentence_similarity(sentence_keyword, student_keyword) > max_score:
                    max_score = sentence_similarity(sentence_keyword, student_keyword)
                    best = student_keyword
            total += max_score
            print(sentence_keyword, ",", best, ",", max_score)
        print(total / len(sentence_keywords))
        grand_total += total / len(sentence_keywords)

    print(grand_total / len(model_answer.keys()))
    print(grand_total)
    total_marks = 0
    for keys in model_answer.keys():
        total_marks += float(model_answer[keys])
ok = st.button("Predict marks")
if (ok):
    st.subheader(f"Marks obtained: {(round((grand_total)/len(model_answer.keys())*2,2))}")
    st.subheader(f"Maximum marks: {(round(total_marks,2))}")
