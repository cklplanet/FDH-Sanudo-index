# Source: https://huggingface.co/osiria/bert-italian-cased-ner
from transformers import DistilBertTokenizerFast, DistilBertForTokenClassification
from transformers import pipeline

tokenizer = DistilBertTokenizerFast.from_pretrained("osiria/distilbert-italian-cased-ner")
model = DistilBertForTokenClassification.from_pretrained("osiria/distilbert-italian-cased-ner")

ner = pipeline("ner", model = model, tokenizer = tokenizer, aggregation_strategy="first")

# The recognition of the GPT-corrected text segments is dramatically improved.
# Segment 676, GPT corrected version
text = '''
Præscriptum, ut hæ nuptiæ tali auspicio sint insulæ  
ac stipulate, ut conjugibus ipsis contra regnis et populis sint usui et voluptati, et ceterisque Christianis omnibus pariant et confirmet perpetuam pacem et tranquillitatem. 

Serenissimo Hungariæ Regi.

Ingentem animo concepimus betitiarum, obi primum ex oratoris istius nostris litteris proxime bih divimus nuptias inter Regem Gelisito et serenissimam Mariam Cesaree et Catholicæ Majestatis sororem interque illustrissimum Ferdinandum, ejusdem unicum fratrem et Illustrissimam Bai Annam Majestatis Vestræ sororem auspicatissimum basim celebratas; nam si quas mutua duo ista connubia duosque reges ac principes potentissimos præclarissimis ortis natalibus tam arctissimo nexu copulatos animo voluerit, si sponsas sponsosque etiam virentes et interea ad transigendum hoc auspiciatum connubium, ad procurandam regiam nobiliorem maxime aptos, si fructus denique elæconomos que Christianis omnibus inde proficere diligentius considerarit, nihil . . . reperiet quod sit hoc vere regio matrimonio vel nobilibus vel præclaris vel majore laude dignius. Quare factum est ut per ea quæ semper Serenissimæ Majestatis nostræ progenitores hereditario quodam jure prosecuto sumus, et præsentibus eadem prosequimur benevolentia et observatione. Nihil prius aut antiquius simus arbitri, quod bis nostris litteris eidem Majestati Vestræ etiam atque etiam summopere gratulati, atque eo quod in spe fore ut Majestatis Vostra novo isto adiuncto conjugio, quod fortunatissimum esse et copiosum et optandum, Cesareæ et Catholicæ Majestatis (ut par est) Consilio auctoritate et viribus adiutis, de universa Christianæ religione fidas poterit promoveri.

Serenissimo Regi Ferdinando archiduci Austrie infantis Hispaniarum etc.

Postea quam vobis nuperrime nunciavimus Majestatem Vestram coniunctam esse serenissimæ Anne, serenissimi Hungariæ regis sorori, omnibus speciosissime, itidemque serenissime ille rex Majestatis Vestræ sororem in uxorem accepisse, certe pro nostra erga Catholicam et Cesaream Majestatem perpetua observantia, pariterque erga Majestatem Vestram sincere nostro benevolo spiritu.
'''

results = ner(text)

person_names = list({entity['word'] for entity in results if entity['entity_group'] == 'PER'})
# Output the list of unique person names
print(person_names)

# # Can also print other name entitys
# location_names = list({entity['word'] for entity in results if entity['entity_group'] == 'LOC'})
# organization_names = list({entity['word'] for entity in results if entity['entity_group'] == 'ORG'})
# miscellaneous_names = list({entity['word'] for entity in results if entity['entity_group'] == 'MISC'})
# print(location_names)
# print(organization_names)
# print(miscellaneous_names)