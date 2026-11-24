import streamlit as st
import pickle
import string
from nltk.corpus import stopwords
import nltk
from nltk.stem.porter import PorterStemmer


#Ensure required nltk data is available
nltk.download('puntk_tab')
nltk.download('stopwords')

ps=PorterStemmer()
stop_words=set(stopwords.words('english'))

def transform_text(text):
    text=text.lower()
    text=nltk.word_tokenize(text)

    y=[]
    for i in text:
        if i.isalnum():
            y.append(i)

    text=y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)

#Loading the saved vector and model
tfidf= pickle.load(open('vectorizer.pkl','rb'))
model= pickle.load(open('model.pkl','rb'))

#Streamlit UI

st.title('Email/SMS spam classifier')

input_sms= st.text_area('Enter the message')

if st.button('Predict'):
    #preprocess
    transformed_text= transform_text(input_sms)

    # Vectorize
    vector_input= tfidf.transform([transformed_text])

    #3Predicrt
    result= model.predict(vector_input)[0]

    #Display
    if result==1:
        st.header('spam')
    else:
        st.header('Not Spam')
    