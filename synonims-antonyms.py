import logging
import pprint
import spacy
import sys

from tendo import colorer
from nltk.corpus import wordnet

logging.basicConfig(format="%(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

nlp = spacy.load('en')

while True:

    word = input("\nw:\t")

    doc = nlp(word)
    for tok in doc:
        logger.warning("Treating '{}' as: {}".format(word, tok.pos_))

    synonyms = []
    antonyms = []
    try:
        synsets_ = wordnet.synsets(
            word,
            pos=eval("wordnet.{}".format(tok.pos_))
        )
    except Exception as e:
        logger.error("Error retrieving synsets for {} as a '{}': {}".format(
            word,
            tok.pos_,
            e
        ))
        continue

    for syn in synsets_:
        logger.info("\n{0} {1}: {2} {0}".format(
            "-" * 20,
            syn.name(),
            syn.definition()
        ))
        for l in syn.lemmas():
            sim = syn.wup_similarity(synsets_[0])
            if sim:
                print("{} & {} = {}".format(syn.name(), l.name(), sim))
                if sim > 0.6:
                    synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())

    logger.info("Synonyms:")
    print(pprint.pformat(
        set(synonyms)
    ))
    logger.info("Antonyms:")
    print(pprint.pformat(
        set(antonyms)
    ))
