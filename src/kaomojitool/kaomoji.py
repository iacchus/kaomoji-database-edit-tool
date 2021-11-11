import base64
from hashlib import sha256
from typing import Union

# let's make a notebook of exceptions here: we can use it later or not

class KaomojiDBKaomojiExists(Exception):
    description="Kaomoji already exists in the KaomojiDB"
    def __init__(self, *args, **kwargs):
        super().__init__(self.description, *args, **kwargs)

class KaomojiDBKaomojiDoesntExist(Exception):
    description="Kaomoji doesn't exist in the KaomojiDB"
    def __init__(self, *args, **kwargs):
        super().__init__(self.description, *args, **kwargs)

class KaomojiKaomojiKeywordExists(Exception):
    description="The keyword already exists in the Kaomoji"
    def __init__(self, *args, **kwargs):
        super().__init__(self.description, *args, **kwargs)

class KaomojiKaomojiKeywordDoesntExist(Exception):
    description="The keyword doesn't already exists in the Kaomoji"
    def __init__(self, *args, **kwargs):
        super().__init__(self.description, *args, **kwargs)


class Kaomoji:
    """Represents a Kaomoji entity."""

    code: str = str()  # unicode of the kaomoji
    keywords: list[str] = list()  # list of strings

    def __init__(self, code=None, keywords=None, line_entry=None):

        if line_entry:
            self.from_line_entry(line_entry=line_entry)

        elif code:
            self.code = code
            self.add_keywords(keywords)

        self._make_inits()

    def add_keyword(self, keyword: str) -> None:
        """Adds a keyword to this kaomoji entity."""

        if keyword and not keyword in self.keywords:
            self.keywords.append(keyword.strip())

    def add_keywords(self, keywords: Union[str, list, None]= None) -> None:

        if not keywords:
            keyword_list = []
        elif isinstance(keywords, str):
            keyword_list = [kw.strip() for kw in keywords.split(',')]
        elif isinstance(keywords, list):
            keyword_list = keywords
        else:
            raise TypeError("keywords is not str | list")

        resume = list(set(self.keywords + keyword_list))  # remove duplicates

        while '' in resume:
            resume.remove('')

        self.keywords = resume

    def from_line_entry(self, line_entry: str):
        """Formats the database line entry as a Kaomoji instance."""

        self.code = str()  # unicode of the kaomoji
        self.keywords = list()  # list of strings

        line = line_entry.strip()

        code, *keywords_str = line.split('\t', maxsplit=1)
        self.code = code
        self.add_keywords(*keywords_str)

        self._make_inits()

        return self


    def remove_keyword(self, keyword: str) -> None:
        """Removes a keyword to this kaomoji entity."""

        if keyword in self.keywords:
            # self.keywords.remove(keyword.strip())
            self.keywords.remove(keyword.strip())

    def remove_keywords(self, keywords: Union[str, list, None]) -> None:

        if not keywords:
            keyword_list = []
        elif isinstance(keywords, str):
            keyword_list = [kw.strip() for kw in keywords.split(',')]
        elif isinstance(keywords, list):
            keyword_list = keywords
        else:
            raise TypeError("keywords is not str | list")

        for keyword in keyword_list:
            kw = keyword.strip()

            print("KEYWORD", kw)
            print("self.KWYWORDS", self.keywords)
            if kw in self.keywords:
                self.keywords.remove(kw)

    def to_line_entry(self, self_register=False) -> str:
        """Formats the current Kaomoji instance as a database line entry."""

        code = self.code
        keywords_str = ", ".join([keyword.strip()
                                  for keyword in self.keywords])
        line_entry = "{code}\t{keywords_str}\n"\
            .format(code=code, keywords_str=keywords_str)

        if self_register:
            self.line_entry = line_entry

        return line_entry

    def _make_hash(self, code, self_register=False) -> int:
        """Gives a UUID for a given kaomoji, for comparison.

        It is the base10 of the sha256 digest of the kaomoji code:
            HASH = INT10(SHA256(BYTES(UNICODE_KAOMOJI_CODE_UTF8)))

        With this we can know if some emoji is already on the DATABASE, so to
            append keywords to it.
        """

        code_bytes = code.encode("utf-8")
        the_hash = sha256(code_bytes).hexdigest()

        # the_hash = int(code_sha256_hex_digestion, base=16)

        if self_register:
            self.hash = the_hash

        return the_hash

    # def _make_hash(self, code, self_register=False) -> int:
    #     """Gives a UUID for a given kaomoji, for comparison.
    #
    #     It is the base10 of the sha256 digest of the kaomoji code:
    #         HASH = INT10(SHA256(BYTES(UNICODE_KAOMOJI_CODE_UTF8)))
    #
    #     With this we can know if some emoji is already on the DATABASE, so to
    #         append keywords to it.
    #     """
    #
    #     code_bytes = code.encode("utf-8")
    #     code_sha256_hex_digestion = sha256(code_bytes).hexdigest()
    #
    #     the_hash = int(code_sha256_hex_digestion, base=16)
    #
    #     if self_register:
    #         self.hash = the_hash
    #
    #     return the_hash


    def _make_shortcode(self, code, self_register=False) -> str:
        """Generates a base64 shortcode to the kaomoji's code
        """

        code_bytes = code.encode("utf-8")

        b64_shortcode = base64.b64encode(code_bytes)

        if self_register:
            self.shortcode = b64_shortcode

        return b64_shortcode

    def _make_inits(self):
        if self.code:
            self.hash = self._make_hash(code=self.code)
            self.shortcode = self._make_shortcode(code=self.code)

    def _hash_to_shortcode(self):
        pass

    def _shortcode_to_hash(self):
        pass

    def __eq__(self, other):
        """ Implements the == (equality) operator to compare two Kaomoji
                instances.
        """

        return hash(self) == hash(other)

    def __hash__(self):
        """ Implements hash() which makes a given emoji to be compared as a
                numeric entity.
        """

        return self.hash

    def __repr__(self):
        """ Implements a repr() pythonic programmatic representation of the
                Kaomoji entity.
        """

        return "<Kaomoji `{}'; kwords: `{}'>".format(self.code, self.keywords)

    def __str__(self):
        """Implements a str() string representation of the kaomoji."""

        return self.code


class KaomojiDB:
    """Offers facilities to edit and check the DB file."""

    def __init__(self, filename=None) -> None:
        """
        Args:
            filename (str): The filename of the splatmoji database to be read.

        Attributes:
            filename (str): the filename of the database file.
            kaomojis (dict): a dictionary which the key is the kaomoji code,
                and the value is a list of keywords, eg.:
                    kaomojis = dict({'o_o': ['keyword 1', 'keyword 2'],
                                    '~_o': ['keywordd', 'keyy2', 'etc']})
        """
        if filename:
            self.load_file(filename=filename)

    def load_file(self, filename: str) -> None:
        """ Loads a db file reading it in the format usable by KaomojiDB class.
        """

        self.filename = filename
        self.kaomojis = dict()
        self.entry_num = int()

        # TODO: check here for errors
        db_file = open(filename, "r")
        #with open(filename) as dbfile:
        lines = db_file.readlines()

        for line in lines:

            # processed_line = line.strip().split("\t", maxsplit=1)
            # if len(processed_line) == 2:
            #     code, keywords = processed_line
            # else:
            #     code, *throwaway = processed_line
            #     keywords = None
            #
            # kaomoji = Kaomoji(code=code, keywords=keywords)
            # kaomoji = Kaomoji().from_line_entry(line_entry=line)
            kaomoji = Kaomoji(line_entry=line)

            self.kaomojis.update({kaomoji.code: kaomoji})

        self.entry_num = len(self.kaomojis)

    def write(self, filename: str=None) -> None:
        """Writes a db file with the changes made."""

        if not filename:
            filename = self.filename

        database_file = open(filename, "w")

        for kaomoji in self.kaomojis.values():
            database_entry_line = kaomoji.to_line_entry()
            database_file.write(database_entry_line)

        database_file.close()
        self.load_file(filename=self.filename)

    def kaomoji_exists(self, kaomoji: Kaomoji) -> bool:
        """Checks if a kaomoji exists already in the database."""

        if kaomoji.code in self.kaomojis:
                return True

        return False

    def add_kaomoji(self, kaomoji: Kaomoji) -> Kaomoji:
        """Adds a Kaomoji to the database."""

        self.kaomojis.update({kaomoji.code: kaomoji})

        return self.kaomojis[kaomoji.code]

    def get_kaomoji(self, by_entity: Union[Kaomoji, str, int]) ->\
                                                        Union[Kaomoji, None]:

        # Kaomoji entity
        if isinstance(by_entity, Kaomoji):

            if by_entity.code in self.kaomojis:
                return self.kaomojis[by_entity.code]

        # str, unicode
        elif isinstance(by_entity, str):

            if by_entity in self.kaomojis:
                return self.kaomojis[by_entity]

        # int, numeric hash
        elif isinstance(by_entity, int):

            for kaomoji in self.kaomojis.values():
                if the_hash == kaomoji.hash:
                    return kaomoji
        else:
            raise TypeError("by_entity is not Kaomoji | str | int")

        return None

    def get_kaomoji_by_code(self, code: str) -> Union[Kaomoji, None]:
        """Gets a Kaomoji with it's current keywords from the database."""

        if code in self.kaomojis:
            return self.kaomojis[code]

        return None

    def get_kaomoji_by_kaomoji(self, other: Kaomoji) -> Union[Kaomoji, None]:
        """Gets a Kaomoji with it's current keywords from the database."""

        if other.code in self.kaomojis:
            return self.kaomojis[other.code]

        return None

    def get_kaomoji_by_hash(self, the_hash: int) -> Union[Kaomoji, None]:
        """Gets a Kaomoji with it's current keywords from the database."""

        for kaomoji in self.kaomojis.values():
            if the_hash == kaomoji.hash:
                return kaomoji

        return None

    def remove_kaomoji(self, kaomoji: Kaomoji) -> None:
        """Removes a Kaomoji from the database."""

        if kaomoji.code in self.kaomojis:
            self.kaomojis.pop(kaomoji.code)

    def update_kaomoji(self, kaomoji: Kaomoji) -> Kaomoji:
        """Updates keywords to database."""

        self.kaomojis.update({kaomoji.code: kaomoji})

        return self.kaomojis[kaomoji.code]

    def compare(self, other, diff_type="additional") -> dict[str: Kaomoji]:
        """Compares two KaomojiDB instances."""

        if not isinstance(other, KaomojiDB):
            raise TypeError("other is not a KaomojiDB")

        other_extra_dict = dict()
        self_extra_dict = dict()
        difference_dict = dict()

        # other_extra - other has and self doesn't
        for kaomoji_code in other.kaomojis:
            if kaomoji_code not in self.kaomojis:
                other_extra_kaomoji = other.kaomojis[kaomoji_code]
                other_extra_dict.update({kaomoji_code: different})

            else:
                for keyword in other.kaomojis[kaomoji_code].keywords:
                    if not keyword in self.kaomojis[kaomoji_code].keywords:
                        if not kaomoji_code in other_extra_dict:
                            other_extra_kaomoji = Kaomoji(code=kaomoji_code, keywords=list())
                            other_extra_dict.update({kaomoji_code: other_extra_kaomoji})
                        other_extra_dict[kaomoji_code].keywords.append(keyword)

        # self_extra - self has and other doesn't
        for kaomoji_code in self.kaomojis:
            if kaomoji_code not in other.kaomojis:
                self_extra_kaomoji = self.kaomojis[kaomoji_code]
                self_extra_dict.update({kaomoji_code: self_extra_kaomoji})

            else:
                for keyword in self.kaomojis[kaomoji_code].keywords:
                    if not keyword in other.kaomojis[kaomoji_code].keywords:
                        if not kaomoji_code in self_extra_dict:
                            self_extra_kaomoji = Kaomoji(code=kaomoji_code, keywords=list())
                            self_extra_dict.update({kaomoji_code: self_extra_kaomoji})
                        self_extra_dict[kaomoji_code].keywords.append(keyword)

        # difference between both
        difference_dict.update(other_extra_dict)
        difference_dict.update(self_extra_dict)

        diff_types = {
            "additional": other_extra_dict,
            "difference": difference_dict,
            "exclusive": self_extra_dict,
        }

        return diff_types[diff_type]
