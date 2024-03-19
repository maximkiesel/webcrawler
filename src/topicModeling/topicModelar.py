import re
from gensim.utils import simple_preprocess
import nltk
from nltk.corpus import stopwords
from gensim.corpora import Dictionary
from gensim.models import LdaModel, CoherenceModel

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

nltk.download('stopwords')
stop_words = stopwords.words('english')


def sent_to_words(sentence):
    return simple_preprocess(str(sentence), deacc=True)


def remove_stopwords(text):
    words = simple_preprocess(str(text))
    filtered_words = [word for word in words if word not in stop_words]
    return filtered_words


def model_topics(title, abstract):
    temp = title + abstract
    print(temp)
    # Remove punctuation
    processed_text = re.sub('[,.!?]', '', temp)
    # Convert to lowercase
    processed_text = processed_text.lower()
    # Tokenize processed text
    tokens = sent_to_words(processed_text)
    # remove stop words from tokens
    filtered_tokens = remove_stopwords(tokens)

    # convert to dictionary
    dictionary = Dictionary([filtered_tokens])

    # Convert the list of words into a bag-of-words representation
    bow_corpus = [dictionary.doc2bow(words) for words in [filtered_tokens]]

    # Running and Training LDA model
    lda_model = LdaModel(bow_corpus, num_topics=1, id2word=dictionary, passes=30)

    topics_dicts = []
    counter = 0
    # format the data so that it can be saved in the database
    for topic in lda_model.print_topics():
        topics_list = []
        for term in topic[1].split(" + "):
            weight, word = term.split("*")
            weight = float(weight.strip())
            word = word.strip()[1:-1]
            topics_list.append({'keyword': word, 'keywordValue': weight})
        topics_dicts.append({"topic": topics_list})
        counter += 1

    return topics_dicts


def calculate_coherence(text, num_topics):
    temp = text
    # Remove punctuation
    processed_text = re.sub('[,.!?]', '', temp)
    # Convert to lowercase
    processed_text = processed_text.lower()
    # Tokenize processed text
    tokens = sent_to_words(processed_text)
    # remove stop words from tokens
    filtered_tokens = remove_stopwords(tokens)

    # convert to dictionary
    dictionary = Dictionary([filtered_tokens])

    # Convert the list of words into a bag-of-words representation
    bow_corpus = [dictionary.doc2bow(words) for words in [filtered_tokens]]

    # Running and Training LDA model
    lda_model = LdaModel(bow_corpus, num_topics=num_topics, id2word=dictionary, passes=20)
    coherence_model = CoherenceModel(model=lda_model, corpus=bow_corpus, texts=[filtered_tokens], coherence='c_v')
    return lda_model, coherence_model


def test_coherence(text):
    text1 = "Re-Examining Inequalities in Computer Science Participation from a Bourdieusian Sociological PerspectiveConcerns about participation in computer science at all levels of education continue to rise, despite the substantial efforts of research, policy, and world-wide education initiatives. In this paper, which is guided by a systematic literature review, we investigate the issue of inequalities in participation by bringing a theoretical lens from the sociology of education, and particularly, Bourdieu’s theory of social reproduction. By paying particular attention to Bourdieu’s theorising of capital, habitus, and field, we first establish an alignment between Bourdieu’s theory and what is known about inequalities in computer science (CS) participation; we demonstrate how the factors affecting participation constitute capital forms that individuals possess to leverage within the computer science field, while students’ views and dispositions towards computer science and scientists are rooted in their habitus which influences their successful assimilation in computer science fields. Subsequently, by projecting the issue of inequalities in CS participation to Bourdieu’s sociological theorisations, we explain that because most interventions do not consider the issue holistically and not in formal education settings, the reported benefits do not continue in the long-term which reproduces the problem. Most interventions have indeed contributed significantly to the issue, but they have either focused on developing some aspects of computer science capital or on designing activities that, although inclusive in terms of their content and context, attempt to re-construct students’ habitus to “fit” in the already “pathologized” computer science fields. Therefore, we argue that to contribute significantly to the equity and participation issue in computer science, research and interventions should focus on restructuring the computer science field and the rules of participation, as well as on building holistically students’ computer science capital and habitus within computer science fields.Concerns about participation in computer science at all levels of education continue to rise, despite the substantial efforts of research, policy, and world-wide education initiatives. In this paper, which is guided by a systematic literature review, we investigate the issue of inequalities in participation by bringing a theoretical lens from the sociology of education, and particularly, Bourdieu’s theory of social reproduction. By paying particular attention to Bourdieu’s theorising of capital, habitus, and field, we first establish an alignment between Bourdieu’s theory and what is known about inequalities in computer science (CS) participation; we demonstrate how the factors affecting participation constitute capital forms that individuals possess to leverage within the computer science field, while students’ views and dispositions towards computer science and scientists are rooted in their habitus which influences their successful assimilation in computer science fields. Subsequently, by projecting the issue of inequalities in CS participation to Bourdieu’s sociological theorisations, we explain that because most interventions do not consider the issue holistically and not in formal education settings, the reported benefits do not continue in the long-term which reproduces the problem. Most interventions have indeed contributed significantly to the issue, but they have either focused on developing some aspects of computer science capital or on designing activities that, although inclusive in terms of their content and context, attempt to re-construct students’ habitus to “fit” in the already “pathologized” computer science fields. Therefore, we argue that to contribute significantly to the equity and participation issue in computer science, research and interventions should focus on restructuring the computer science field and the rules of participation, as well as on building holistically students’ computer science capital and habitus within computer science fields."
    coherence_values = []
    model_list = []

    limit = 11
    start = 1
    step = 1

    for num_topics in range(start, limit, step):
        lda_model, coherence_model = calculate_coherence(text, num_topics)
        model_list.append(lda_model)
        coherence_values.append(coherence_model.get_coherence())
        print(coherence_model.get_coherence())
        print(num_topics)


    x = range(start, limit, step)
    plt.ylim([0, 1])
    plt.plot(x, coherence_values)
    plt.xlabel("Anzahl der Themen")
    plt.ylabel("Coherence score")
    plt.legend(("coherence_values"), loc='best')
    plt.show()

if __name__ == '__main__':
    test_coherence("asd")
