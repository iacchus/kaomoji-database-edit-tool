from hashlib import sha256

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

    code = str()  # unicode of the kaomoji
    keywords = list()  # list of strings

    def __init__(self, code=None, keywords=None):


        self.code = code if code else None

        if isinstance(keywords, str):
            self.add_keywords_str(keywords)
        elif isinstance(keywords, list):
            self.add_keywords_list(keywords)

        self.hash = self._makehash(code)

    def add_keyword(self, keyword) -> None:
        """Adds a keyword to this kaomoji entity."""

        if not keyword in self.keywords:
            self.keywords.append(keyword.strip())

    def add_keywords_str(self, keywords_str: str) -> None:

        if not isinstance(keywords_str, str):
            raise TypeError("keywords_str is not a str")

        keywords = [keyword.strip() for keyword in keywords_str.split(',')]
        self.add_keywords_list(keywords_list=keywords)

    def add_keywords_list(self, keywords_list: list[str]) -> None:

        if not isinstance(keywords_list, list):
            raise TypeError("keywords_list is not a list")

        resume = list(set(self.keywords + keywords_list))

        self.keywords = resume

    def from_line_entry(self, line_entry: str):

        self.code = str()  # unicode of the kaomoji
        self.keywords = list()  # list of strings

        line = line_entry.strip()
        code, keywords_str = line_entry.split('\t', maxsplit=1)
        self.code = code
        self.add_keywords_str(keywords_str)

        self.hash = self._makehash(code)

    def remove_keyword(self, keyword) -> None:
        """Removes a keyword to this kaomoji entity."""

        if keyword in self.keywords:
            self.keywords.remove(keyword.strip())

    def remove_keywords_str(self, keywords_str: str) -> None:

        if not isinstance(keywords_str, str):
            raise TypeError("keywords_str is not a str")

        keywords = [keyword.strip() for keyword in keywords_str.split(',')]
        self.add_keywords_list(keywords_list=keywords)

    def remove_keywords_list(self, keywords_list: list[str]) -> None:

        if not isinstance(keywords_list, list):
            raise TypeError("keywords_list is not a list")

        for keyword in keywords_list:
            kw = keyword.strip()
            if kw in self.keywords:
                self.keywords.remove(kw)

    def to_line_entry(self, register=True):
        code = self.code
        keywords_str = ", ".join([keyword.strip()
                                  for keyword in self.keywords])
        line_entry = "{code}\t{keywords_str}\n"\
            .format(code=code, keywords_str=keywords_str)

        if register:
            self.line_entry = line_entry

        return line_entry

    def _makehash(self, code) -> int:
        """Gives a UUID for a given kaomoji, for comparison.

        It is the base10 of the sha256 digest of the kaomoji code:
            HASH = INT10(SHA256(BYTES(UNICODE_KAOMOJI_CODE_UTF8)))

        With this we can know if some emoji is already on the DATABASE, so to
            append keywords to it.
        """

        code_bytes = code.encode("utf-8")
        code_sha256_hex_digestion = sha256(code_bytes).hexdigest()

        the_hash = int(code_sha256_hex_digestion, base=16)

        return the_hash

    def _make_shortcode(self, thehash=None) -> str:
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

            #self.filename = filename
            #self.load_file(filename=self.filename)
            self.load_file(filename=filename)

    def load_file(self, filename) -> None:
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

            processed_line = line.strip().split("\t", maxsplit=1)
            if len(processed_line) == 2:
                code, keywords = processed_line
            else:
                code, *throwaway = processed_line
                keywords = None

            kaomoji = Kaomoji(code=code, keywords=keywords)

            self.kaomojis.update({code: kaomoji})

        self.entry_num = len(self.kaomojis)

    def write(self, filename=None) -> None:
        """Writes a db file with the changes made."""

        if not filename:
            filename = self.filename

        db_file = open(filename, "w")

        for code, kaomoji in self.kaomojis.items():
            #code = kaomoji.code
            keywords_string = ", ".join(kaomoji.keywords)
            db_line = "{0}\t{1}\n".format(code, keywords_string)
            db_file.write(db_line)

        db_file.close()
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

    def get_kaomoji_by_code(self, code: str) -> Kaomoji:
        """Gets a Kaomoji with it's current keywords from the database."""

        return self.kaomojis[code]

    def get_kaomoji_by_kaomoji(self, other: Kaomoji) -> Kaomoji:
        """Gets a Kaomoji with it's current keywords from the database."""

        return self.kaomojis[other.code]

    def get_kaomoji_by_hash(self, thehash: int) -> Kaomoji:
        """Gets a Kaomoji with it's current keywords from the database."""

        for kaomoji in self.kaomojis.values():
            if thehash == kaomoji.hash:
                return kaomoji

    def remove_kaomoji(self, kaomoji: Kaomoji) -> None:
        """Removes a Kaomoji from the database."""

        if kaomoji.code in self.kaomojis:
            self.kaomojis.pop(kaomoji.code)

    def update_kaomoji(self, kaomoji: Kaomoji) -> Kaomoji:
        """Updates keywords to database."""

        self.kaomojis.update({kaomoji.code: kaomoji})

        return self.kaomojis[kaomoji.code]

    def compare(self, other) -> dict[str: Kaomoji]:
        """Compares two KaomojiDB instances."""

        if not isinstance(other, KaomojiDB):
            raise TypeError("other is not a KaomojiDB")

        differences_dict = dict()

        for kaomoji_code in other.kaomojis:
            if kaomoji_code not in self.kaomojis:
                different = other.kaomojis[kaomoji_code]
                differences_dict.update({kaomoji_code: different})

            else:
                for keyword in other.kaomojis[kaomoji_code].keywords:
                    if not keyword in self.kaomojis[kaomoji_code].keywords:
                        if not kaomoji_code in differences_dict:
                            different = Kaomoji(code=kaomoji_code, keywords=list())
                            differences_dict.update({kaomoji_code: different})
                        differences_dict[kaomoji_code].keywords.append(keyword)

        return differences_dict
