import pymongo
import re
import nltk
import warnings
warnings.filterwarnings("ignore")
from nltk.tokenize import regexp_tokenize
from nltk.corpus import stopwords

nltk.download('stopwords')
from nltk.stem import PorterStemmer
from spellchecker import SpellChecker


client = pymongo.MongoClient("mongodb+srv://pranavi:YdLryCPrah1fH57p@cluster0.nl14hmc.mongodb.net/?retryWrites=true&w=majority")

# function to fix word lengthening
def fixLengthening(word):
    fix = re.compile(r"(.)\1{2,}")
    return fix.sub(r"\1\1", word)

print(client.list_database_names())
db = client.quiz
print(db.list_collection_names())

db = client.get_database("quiz")
records = db["quiz"]

total = db.quiz.count_documents({})
# data_s = [
#
#     {"question":"How many days are there in weeks",
#      "answer": "There are seven days"},
#
#     {"question": "Who is the current president of USA?",
#      "answer":"Boe Joe Biden"} ,
#
#     {"question": "What is the use of computer?",
#      "answer": "A computer is an electronic device that manipulates information, or data. It has the ability to store, retrieve, and process data. You may already know that you can use a computer to type documents, send email, play games, and browse the Web"},
#
#     {"question": "what is the use of calculator?",
#      "answer" : "The purpose of a calculator is to do correct calculations.\n\nTo do calculators like addition, subtraction, multiplication, and division.\n\nTo do basic mathematical operation.\n "
#      },
#
#     {"question": "what is the use of bus?",
#      "answer":"Buses may be used for scheduled bus transport, scheduled coach transport, school transport, private hire, or tourism; promotional buses may be used for political campaigns and others are privately operated for a wide range of purposes, including rock and pop band tour vehicles."
#      }
# ]
#
#
# quiz = db.quiz
#
#
# quiz_z = quiz.insert_many(data_s)





import random
from random import randrange

cur = db.quiz.find({},{"_id":0})
x = list(cur)


# print(x[1])

# rand_sentence = random.choice(x)
i = randrange(5)
rand = str(x[i]["question"])

#rand = db.sentences.aggregate([{"$sample": {"size": 1}}])
print(rand)

model = rand


# TODO: catch zero division error when tokens list is empty
student = input("Enter the student answer ")

# BEGINNING OF NLP PIPELINE
# step1: convert both sentences to lower case

#model = model.lower()
model = str(x[i]["answer"])
student = student.lower()
# step2: removing numbers
model = re.sub(r'\d+', '', model)
student = re.sub(r'\d+', '', student)
# step3: Tokenization AND removing punctuations and white spaces
model_tokens = regexp_tokenize(model, pattern="\w+")
student_tokens = regexp_tokenize(student, pattern="\w+")
# step4: stop words removal
listOfSw = stopwords.words('english')
modelPostSwr = [word for word in model_tokens if word not in listOfSw]
studentPostSwr = [word for word in student_tokens if word not in listOfSw]
# step5: fixing word lenghtening
modelPostFl = [fixLengthening(word) for word in modelPostSwr]
studentPostFl = [fixLengthening(word) for word in studentPostSwr]
# step6: spell corrections
spell = SpellChecker()
modelPostSc = [spell.correction(word) for word in modelPostFl]
studentPostSc = [spell.correction(word) for word in studentPostFl]
print(modelPostSc)
print(studentPostSc)
# step7: stemming
porter = PorterStemmer()
modelPostStem = [porter.stem(word) for word in modelPostSc]
studentPostStem = [porter.stem(word) for word in studentPostSc]
# step8: similarity comparison
set1 = []
set2 = []
unionVector = list(set().union(modelPostStem, studentPostStem))
for word in unionVector:
    if word in modelPostStem:
        set1.append(1)
    else:
        set1.append(0)
    if word in studentPostStem:
        set2.append(1)
    else:
        set2.append(0)
comp = 0
for i in range(len(unionVector)):
    comp += set1[i] * set2[i]
cosineSimilarity = comp / float((sum(set1) * sum(set2)) ** 0.5)
# step9: result report with similarity score and pass or fail
perc = 100 * cosineSimilarity
if perc >= 70.0:
    print("PASS with a score of: " + str(round(perc, 2)) + "%")
else:
    print("FAIL with a score of: " + str(round(perc, 2)) + "%")