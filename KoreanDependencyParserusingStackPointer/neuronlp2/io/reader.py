__author__ = 'max'

from .instance import DependencyInstance, NERInstance
from .instance import Sentence
from .conllx_data import ROOT, ROOT_POS, ROOT_CHAR, ROOT_TYPE, END, END_POS, END_CHAR, END_TYPE
from . import utils


class CoNLLXReader(object):
    def __init__(self, file_path, word_alphabet, char_alphabet, pos_alphabet, type_alphabet):
        self.__source_file = open(file_path, 'r', encoding='utf-8')
        self.__word_alphabet = word_alphabet
        self.__char_alphabet = char_alphabet
        self.__pos_alphabet = pos_alphabet
        self.__type_alphabet = type_alphabet

    def close(self):
        self.__source_file.close()

    def getNext(self, normalize_digits=True, symbolic_root=False, symbolic_end=False, sent_id=0):
        line = self.__source_file.readline()
        # skip multiple blank lines.
        while len(line) > 0 and len(line.strip()) == 0:
            line = self.__source_file.readline()
        if len(line) == 0:
            return

        lines = []
        while len(line.strip()) > 0:
            if line.strip().startswith("#"):
                line = self.__source_file.readline()
            else:
                line = line.strip()
                lines.append(line.split('\t'))
                line = self.__source_file.readline()

        length = len(lines)
        if length == 0:
            return None

        word_seqs = []
        word_id_seqs = []
        char_seqs = []
        char_id_seqs = []
        pos_seqs = []
        pos_id_seqs = []
        types = []
        type_ids = []
        heads = []

        if symbolic_root:
            word_seqs.append([ROOT, ])
            word_id_seqs.append([self.__word_alphabet.get_index(ROOT), ])
            char_seqs.append([[ROOT_CHAR, ]])
            char_id_seqs.append([[self.__char_alphabet.get_index(ROOT_CHAR), ]])
            pos_seqs.append([ROOT_POS, ])
            pos_id_seqs.append([self.__pos_alphabet.get_index(ROOT_POS), ])
            types.append(ROOT_TYPE)
            type_ids.append(self.__type_alphabet.get_index(ROOT_TYPE))
            heads.append(0)

        for tokens in lines:
            words = []
            word_ids = []
            chars = []
            char_ids = []
            for lemma in tokens[2].split(" "):
                lemma_ = utils.DIGIT_RE.sub("0", lemma) if normalize_digits else lemma
                words.append(lemma_)
                word_ids.append(self.__word_alphabet.get_index(lemma_))
                lemmas = []
                lemma_ids = []
                for char in lemma:
                    lemmas.append(char)
                    lemma_ids.append(self.__char_alphabet.get_index(char))
                if len(chars) > utils.MAX_CHAR_LENGTH:
                    lemmas = lemmas[:utils.MAX_CHAR_LENGTH]
                    lemma_ids = lemma_ids[:utils.MAX_CHAR_LENGTH]
                chars.append(lemmas)
                char_ids.append(lemma_ids)
            if len(words) > utils.MAX_EOJUL_LENGTH:
                words = words[:utils.MAX_EOJUL_LENGTH]
                word_ids = word_ids[:utils.MAX_EOJUL_LENGTH]
            word_seqs.append(words)
            word_id_seqs.append(word_ids)
            char_seqs.append(chars)
            char_id_seqs.append(char_ids)

            poss = []
            pos_ids = []

            for pos in tokens[4].split("+"):
                poss.append(pos)
                pos_ids.append(self.__pos_alphabet.get_index(pos))
            if len(poss) > utils.MAX_POS_LENGTH:
                poss = poss[:utils.MAX_POS_LENGTH]
                pos_ids = pos_ids[:utils.MAX_POS_LENGTH]

            pos_seqs.append(poss)
            pos_id_seqs.append(pos_ids)

            #word = utils.DIGIT_RE.sub("0", tokens[1]) if normalize_digits else tokens[1]
            #pos = tokens[4]
            head = int(tokens[6])
            type = tokens[7]

            #words.append(word)
            #word_ids.append(self.__word_alphabet.get_index(word))

            #postags.append(pos)
            #pos_ids.append(self.__pos_alphabet.get_index(pos))

            types.append(type)
            type_ids.append(self.__type_alphabet.get_index(type))

            heads.append(head)

        if symbolic_end:
            word_seqs.append([END, ])
            word_id_seqs.append([self.__word_alphabet.get_index(END), ])
            char_seqs.append([END_CHAR, ])
            char_id_seqs.append([self.__char_alphabet.get_index(END_CHAR), ])
            pos_seqs.append([END_POS, ])
            pos_id_seqs.append([self.__pos_alphabet.get_index(END_POS), ])
            types.append(END_TYPE)
            type_ids.append(self.__type_alphabet.get_index(END_TYPE))
            heads.append(0)

        return DependencyInstance(Sentence(word_seqs, word_id_seqs, char_seqs, char_id_seqs, sent_id, lines), pos_seqs, pos_id_seqs, heads, types, type_ids)


class CoNLL03Reader(object):
    def __init__(self, file_path, word_alphabet, char_alphabet, pos_alphabet, chunk_alphabet, ner_alphabet):
        self.__source_file = open(file_path, 'r')
        self.__word_alphabet = word_alphabet
        self.__char_alphabet = char_alphabet
        self.__pos_alphabet = pos_alphabet
        self.__chunk_alphabet = chunk_alphabet
        self.__ner_alphabet = ner_alphabet

    def close(self):
        self.__source_file.close()

    def getNext(self, normalize_digits=True):
        line = self.__source_file.readline()
        # skip multiple blank lines.
        while len(line) > 0 and len(line.strip()) == 0:
            line = self.__source_file.readline()
        if len(line) == 0:
            return None

        lines = []
        while len(line.strip()) > 0:
            line = line.strip()
            line = line.decode('utf-8')
            lines.append(line.split(' '))
            line = self.__source_file.readline()

        length = len(lines)
        if length == 0:
            return None

        words = []
        word_ids = []
        char_seqs = []
        char_id_seqs = []
        postags = []
        pos_ids = []
        chunk_tags = []
        chunk_ids = []
        ner_tags = []
        ner_ids = []

        for tokens in lines:
            chars = []
            char_ids = []
            for char in tokens[1]:
                chars.append(char)
                char_ids.append(self.__char_alphabet.get_index(char))
            if len(chars) > utils.MAX_CHAR_LENGTH:
                chars = chars[:utils.MAX_CHAR_LENGTH]
                char_ids = char_ids[:utils.MAX_CHAR_LENGTH]
            char_seqs.append(chars)
            char_id_seqs.append(char_ids)

            word = utils.DIGIT_RE.sub(b"0", tokens[1]) if normalize_digits else tokens[1]
            pos = tokens[2]
            chunk = tokens[3]
            ner = tokens[4]

            words.append(word)
            word_ids.append(self.__word_alphabet.get_index(word))

            postags.append(pos)
            pos_ids.append(self.__pos_alphabet.get_index(pos))

            chunk_tags.append(chunk)
            chunk_ids.append(self.__chunk_alphabet.get_index(chunk))

            ner_tags.append(ner)
            ner_ids.append(self.__ner_alphabet.get_index(ner))

        return NERInstance(Sentence(words, word_ids, char_seqs, char_id_seqs), postags, pos_ids, chunk_tags, chunk_ids,
                           ner_tags, ner_ids)
