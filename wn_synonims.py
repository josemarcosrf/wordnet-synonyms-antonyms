import argparse
import logging
import pprint
import spacy

from tendo import colorer
from nltk.corpus import wordnet


logging.basicConfig(format="%(message)s")
logger = logging.getLogger()


class WNSynonims:

    def __init__(self, lang_code):
        self.valid_languages = ['en']

        # init the nlp module
        if lang_code in self.valid_languages:
            self.nlp = spacy.load(lang_code)
        else:
            raise ValueError("language '{}' is not a valid language code".format(lang_code))

    @staticmethod
    def wordnet_sim(syn1, syn2, lemma, sim_type='path'):
        if sim_type == "path":
            sim = syn1.path_similarity(syn2)
            logger.debug("{} & {} => path sim: {}".format(
                syn1.name(), syn2.name(), sim
            ))
        elif sim_type == "wup":
            sim = syn1.wup_similarity(syn2)
            logger.debug("{} & {} => wu-palmer sim: {}".format(
                syn1.name(), syn2.name(), sim
            ))
        elif sim_type == "lch":
            sim = syn1.lch_similarity(syn2)
            logger.debug("{} & {} => lch-sim: {}".format(
                syn1.name(), syn2.name(), sim
            ))
        else:
            raise Exception("'{}' is not a valid similarity type.".format(sim_type))

        return sim

    def search(self, word):

        # POS tagging
        doc = self.nlp(word)
        for tok in doc:
            logger.warning("Treating '{}' as: {}".format(word, tok.pos_))

        synonyms = []
        antonyms = []
        synsets_ = []
        try:
            synsets_ = wordnet.synsets(
                word,
                pos=eval("wordnet.{}".format(tok.pos_))
            )
            if len(synsets_) == 0:
                # try with Morphy. e.g.: 'denied' -> 'deny'
                word_morphed = wordnet.morphy(word)
                logger.warning("Morphing {} to {}".format(word, word_morphed))
                synsets_ = wordnet.synsets(
                    word_morphed,
                    pos=eval("wordnet.{}".format(tok.pos_))
                )
        except Exception as e:
            logger.error("Error retrieving synsets for {} "
                         "as a '{}': {}".format(word, tok.pos_, e))
            logger.exception(e)

        try:
            for syn in synsets_:
                logger.info("\n{0} {1}: {2} {0}".format(
                    "-" * 20,
                    syn.name(),
                    syn.definition()
                ))
                for l in syn.lemmas():
                    sim = self.wordnet_sim(syn, synsets_[0], l)
                    if sim and sim > 0.6:
                        synonyms.append(l.name().replace("_", " "))
                    if l.antonyms():
                        antonyms.append(l.antonyms()[0].name().replace("_", " "))

        except Exception as e:
            logger.error("Error while looking for synonyms & antonyms: {}".format(e))
            logger.exception(e)

        return synonyms, antonyms


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', default='en',
                        help="language to explore synsets")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="Set level of logging to debugging")

    return parser.parse_args()


if __name__ == "__main__":

    args = get_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    # init the class
    syns = WNSynonims(args.lang)

    while True:

        word = input("\nw:\t")

        synonyms, antonyms = syns.search(word)

        print("Synonyms: {}".format(
              pprint.pformat(set(synonyms))))
        print("Antonyms: {}".format(
              pprint.pformat(set(antonyms))))
