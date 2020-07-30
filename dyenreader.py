#!/usr/bin/python
from enum import IntFlag
from collections import defaultdict
import regex


class DyenJudge(IntFlag):
    UNKNOWN = 0
    UNIQUE = 1
    COG_CONFIDENT = 2
    COG_DOUBTFUL = 3
    EXCLUSIVE = 4
    NOT_EXCLUSIVE = 5


class CognateGroup:
    def __init__(self, groupId, meaningGroup):
        self.groupId = groupId
        self.meaningGroup = meaningGroup
        self.cogWith = []
        self.words = []

        if groupId == 0:
            self.cogStatus = DyenJudge.UNKNOWN
        elif groupId == 1:
            self.cogStatus = DyenJudge.UNIQUE
        elif groupId < 100:
            self.cogStatus = DyenJudge.COG_CONFIDENT | DyenJudge.EXCLUSIVE
        elif groupId < 200:
            self.cogStatus = DyenJudge.COG_DOUBTFUL | DyenJudge.EXCLUSIVE
        elif groupId < 400:
            self.cogStatus = DyenJudge.COG_CONFIDENT | DyenJudge.NOT_EXCLUSIVE
        elif groupId < 500:
            self.cogStatus = DyenJudge.COG_DOUBTFUL | DyenJudge.NOT_EXCLUSIVE
        else:
            raise Exception('Could not classify type of cognate of CCN #{}'.format(groupId))

    def AllReflexes(self):
        tempList = [word for cogGroups, relType in self.cogWith for word in cogGroups.words if DyenJudge.COG_CONFIDENT in relType or DyenJudge.COG_DOUBTFUL in relType]
        return self.words + tempList

    def AllMembersInLanguages(self, languageNameList):
        """Finds all words in a cognate group within the specified languages
        """
        return [word for word in self.AllReflexes()
                if word.language in languageNameList]



class MeaningGroup:
    def __init__(self, groupId, meaningSense):
        self.groupId = groupId
        self.meaningSense = meaningSense
        self.cognateGroups = []
        self.cognateGroupsById = dict()

    def __str__(self):
        return self.meaningSense

    def __repr__(self):
        return self.__str__()


class Word:
    def __init__(self, word, language, meaningGroup, cognateGroup):
        self.word = regex.sub(r'\([^)]*\)', '', word).strip()
        self.originalRep = word
        self.language = language
        self.meaningGroup = meaningGroup
        self.cognateGroup = cognateGroup

    def __str__(self):
        return "{} ({} '{}'')".format(self.word, self.language, self.meaningGroup.meaningSense)

    def __repr__(self):
        return self.__str__()

    def CogWith(self, otherWord):
        return (otherWord.cognateGroup == self.cognateGroup or
                (otherWord.cognateGroup, DyenJudge.COG_CONFIDENT)
                    in self.cognateGroup.cogWith)

class DyenList:

    def __init__(self):
        self.meaningGroups = []
        self.cognateGroups = []
        self.languages = [
"NEW ENGLISH",
"TAKITAKI",
"WAZIRI",
"ARMENIAN",
"BRAZILIAN",
"PORTUGUESE",
"BULGARIAN",
"UKRAINIAN",
"BYELORUSSIAN",
"EAST CZECH",
"MOD ARMENIAN",
"KHASKURA",
"PANJABI",
"HINDI",
"BENGALI",
"MARATHI",
"PERSIAN",
"ALBANIAN",
"GUJARATI",
"MACEDONIAN",
"TADZIK",
"ALBANIAN SG",
"ALBANIAN C",
"ALBANIAN K",
"ALBANIAN T",
"AFRIKAANS",
"DUTCH",
"DUTCH P",
"FLEMISH",
"FRISIAN",
"FAROESE",
"DANISH",
"SWEDISH",
"RIKSMAL NORWAY",
"MOD ICELANDIC",
"GERMAN",
"BRETON ST",
"BRETON SE",
"BRETON",
"WELSH C",
"WELSH N",
"EIRE",
"IRISH",
"FRENCH",
"CREOLE DF",
"WALLOON",
"PROVENCAL",
"SPANISH",
"CATALAN",
"ITALIAN",
"SARDINIAN C",
"LADIN",
"RUMANIAN",
"AFGHAN",
"BALOCHI",
"WAKHI",
"LAHNDA",
"NEPALI",
"KASHMIRI",
"SINGHALESE",
"GREEK MOD",
"GREEK ML",
"GREEK K",
"GREEK MD",
"GREEK D",
"LITHUANIAN",
"LITHUANIAN X",
"LATVIAN",
"BULGARIAN P",
"BYELORUSSIAN P",
"CZECH",
"CZECH P",
"LUSATIAN LP",
"LUSATIAN UP",
"MACEDONIAN P",
"POLISH",
"POLISH P",
"RUSSIAN",
"RUSSIAN P",
"SERBOCROATIAN",
"SERBOCROATIAN P",
"SLOVAK",
"SLOVAK P",
"SLOVENIAN",
"SLOVENIAN P",
"UKRAINIAN P",
"CREOLE D",
"OSSETIC",
"SARDINIAN N",
"SARDINIAN L",
"ALBANIAN TOP",
"VLACH",
"GYPSY GK",
"SWEDISH UP",
"SWEDISH VL"]
        self.languageWords = defaultdict(list)

    def FindWords(self, searchWord, language):
        return [word for word in self.languageWords[language] if word.word == searchWord]

    def TransformWordsInLanguage(self, languageName, pattern, repl):
        for word in self.languageWords[languageName]:
            word.word = regex.sub(pattern, repl, word.word)

    def ReadFromDyenForm(self, file):
        cogRels = []
        with open(file, 'r') as dyenFile:
            for line in dyenFile:
                # Skip ahead until data begins
                if line == '5. THE DATA\n':
                    next(dyenFile)
                    for line in dyenFile:
                        line = line[:-1]
                        if line[0] == 'a': # Create new meaning group
                            splitLine = line.split()
                            meaningId = splitLine[1]
                            meaningSense = ' '.join(splitLine[2:])
                            meaningGroup = MeaningGroup(int(meaningId) - 1, meaningSense)
                            self.meaningGroups += [meaningGroup]
                        if line[0] == 'b': # Create new cognate group
                            cognateGroup = CognateGroup(int(line[-3:]), meaningGroup)
                            meaningGroup.cognateGroups += [cognateGroup]
                            meaningGroup.cognateGroupsById[int(line[-3:])] = cognateGroup
                            self.cognateGroups += [cognateGroup]
                        if line[0] == 'c':
                            formChar, group1, relType, group2 = line.split()
                            cogRels += [(meaningGroup, int(group1), relType, int(group2))]
                        if line[0:2] == '  ':
                            parts = line[2:].split()
                            datLine = ' '.join(parts[2:])
                            for lang in sorted(self.languages, key=len, reverse=True):
                                if lang in datLine:
                                    langName = lang
                                    wordText = datLine.replace(langName, '').strip()
                                    break
                            assert wordText is not None, "Couldn't find a matching language for {}".format(datLine)
                            if wordText != "":
                                for wordPart in wordText.split(','):
                                    newWord = Word(wordPart, langName, self.meaningGroups[-1], self.cognateGroups[-1])
                                    self.cognateGroups[-1].words += [newWord]
                                    self.languageWords[langName] += [newWord]
        # Parse cognate relations now that all CCNs have been parsed
        try:
            for meaningGroup, group1, relType, group2 in cogRels:
                meaningGroup.cognateGroupsById[group1].cogWith += [(meaningGroup.cognateGroupsById[group2], DyenJudge(int(relType)))]
                meaningGroup.cognateGroupsById[group2].cogWith += [(meaningGroup.cognateGroupsById[group1], DyenJudge(int(relType)))]
        except KeyError as e:
            print("Couldn't find matching CCN #{} in meaning group {}".format(e.args[0], meaningGroup))
            raise
