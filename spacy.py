import spacy
import bs4 as bs  
import urllib.request  
import re  
import nltk
from spacy import displacy
from spacy.matcher import Matcher 

nlp = spacy.load('en_core_web_sm')
doc1 = nlp(u'Hello hi there!')
doc2 = nlp(u'Hello hi there!')
doc3 = nlp(u'Hey whatsup?')
doc4 = nlp(u'How is it going?')
doc5 = nlp(u'How are you doing?')
amazonDoc = nlp(u'You may not transfer outside the Services any software (including related documentation) you obtain from us or third party licensors in connection with the Services without specific authorization to do so.')
appleDoc = nlp(u'You may not transfer, redistribute or sublicense the Licensed Application and, if you sell your Apple Device to a third party, you must remove the Licensed Application from the Apple Device before doing so.')

# print(doc1.similarity(doc2)) # 0.999999954642
# print(doc2.similarity(doc3)) # 0.699032527716
# print(doc1.similarity(doc3)) # 0.699032527716

# print(doc3.similarity(doc4)) # 0.195596
# print(doc5.similarity(doc4)) # 0.8566903441700623 
# print(amazonDoc.similarity(appleDoc)) # 0.5664364642872158

# print(nlp(u'automatic charges').similarity(nlp(u'You will get charged automatically every month'))) # -0.03377581193980206

# ----------------------
nlp = spacy.load('en_core_web_sm')

matcher = Matcher(nlp.vocab)

scrapped_data = urllib.request.urlopen('https://aws.amazon.com/service-terms/')  
article = scrapped_data.read()

parsed_article = bs.BeautifulSoup(article,'lxml')

paragraphs = parsed_article.find_all('p')

article_text = ''

for p in paragraphs:  
    article_text += p.text
    
    
processed_article = article_text.lower()  
processed_article = re.sub('[^a-zA-Z]', ' ', processed_article)  
processed_article = re.sub(r'\s+', ' ', processed_article)

f = open('/Users/sauharda.rajbhandari/Desktop/Amazon AWS ToS.txt', 'r')
processed_article = f.read()

matched_sents = []
appended_sentences = set()

def collect_sents(matcher, doc, i, matches, label='MATCH'):
    match_id, start, end = matches[i]
    span = doc[start:end]  # Matched span
    sent = span.sent  # Sentence containing matched span
    # Append mock entity for match in displaCy style to matched_sents
    # get the match span by ofsetting the start and end of the span with the
    # start and end of the sentence in the doc
    match_ents = [{
        'start': span.start_char - sent.start_char,
        'end': span.end_char - sent.start_char,
        'label': label,
    }]

    if (span.sent not in appended_sentences):
        matched_sents.append({'text': sent.text, 'ents': match_ents})
        appended_sentences.add(span.sent)
    else: 
        for ms in matched_sents:
            if (str(ms['text']) == str(span.sent) and str(span.sent)):
                ms['ents'].append({'start': span.start_char - sent.start_char, 'end': span.end_char - sent.start_char, 'label': label })


words = ['arbitrate', 'arbitration', 'payment', 'store', 'privacy', 'data', 'address', 'security', 'permission', 'download', 'steal', 'keep', 'lawsuit', 'litigate', 'litigation', 'charge', 'force', 'class', 'action', 'class-action']

lemma_pattern = [{'LEMMA': {'IN': [text for text in words]}, 'OP': '?'}, {'ORTH': {'IN': [text for text in words]}, 'OP': '?'}]
we_collect_pattern = [{'POS': 'PRON'}, {'POS': 'ADV', 'OP': '*'}, {'LEMMA': {'IN': ['go', 'will', 'be']}, 'OP': '*'}, {'LEMMA': {'IN': ['store', 'collect', 'save', 'sell']}}, {'OP': '?'}]

matcher.add('Collection matcher', [we_collect_pattern], on_match=lambda a, b, c, d : collect_sents(a, b, c, d, 'Collection match'))
matcher.add('Lemma matcher', [lemma_pattern], on_match=lambda a, b, c, d : collect_sents(a, b, c, d, 'Lemma match'))

article = nlp(processed_article)

matches = matcher(article)
colors = {"Lemma match": "linear-gradient(90deg, #aa9cfc, #fc9ce7)", "Collection match": "linear-gradient(90deg, #aa9cfc, #fc9ce7)"}
options = {"ents": ["Lemma match"], "colors": colors}

displacy.serve(matched_sents, style='ent', manual=True, options=options)