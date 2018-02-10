import logging
import pprint
import spacy
import sys

from tendo import colorer
from nltk.corpus import wordnet

logging.basicConfig(format="%(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def wordnet_sim(syn1, syn2, lemma, sim_type='path'):
    if sim_type == "path":
        sim = syn.path_similarity(syn2)
        logger.debug("{} & {} => path sim: {}".format(
            syn1.name(), syn2.name(), sim
        ))
    elif sim_type == "wup":
        sim = syn.wup_similarity(syn2)
        logger.debug("{} & {} => wu-palmer sim: {}".format(
            syn1.name(), syn2.name(), sim
        ))
    elif sim_type == "lch":
        sim = syn.lch_similarity(syn2)
        logger.debug("{} & {} => lch-sim: {}".format(
            syn1.name(), syn2.name(), sim
        ))
    else:
        raise Exception("'{}' is not a valid similarity type.".format(sim_type))

    return sim


if __name__ == "__main__":

    # Load spacy english model
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

        try:
            for syn in synsets_:
                logger.info("\n{0} {1}: {2} {0}".format(
                    "-" * 20,
                    syn.name(),
                    syn.definition()
                ))
                for l in syn.lemmas():
                    sim = wordnet_sim(syn, synsets_[0], l)
                    if sim > 0.6:
                        synonyms.append(l.name())
                    if l.antonyms():
                        antonyms.append(l.antonyms()[0].name())
        except Exception as e:
            logger.error("Error while looking for synonyms & antonyms: {}".format(e))

        logger.info("Synonyms:")
        print(pprint.pformat(
            set(synonyms)
        ))
        logger.info("Antonyms:")
        print(pprint.pformat(
            set(antonyms)
        ))
