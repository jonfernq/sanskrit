-- create_view_w_dict_meanings.sql

-- Example SQL code to create flashcards from DCS text files
-- and dictionary.csv (SQLite table 'sktdictdcs3' below).
-- The DCS dictionary and text files are joined into a unified view 
-- to create flashcards from. 
-- Any range of stanzas from within the text can be chosen.
-- One can also filter for grammatical attributes or semantic field (using WordNet)

-- I ran this code in SQLiteStudio, not a Python script though that is possible to.
-- 

CREATE VIEW WordsAndMeanings AS
SELECT meghaduta1.TEXT_UNIT,meghaduta1.WORK,meghaduta1.CHAPTER,meghaduta1.VERSE,meghaduta1.HALF_VERSE,meghaduta1.WORD,meghaduta1.SENTENCE_COMPOUND_WORD,meghaduta1.WORD_CITATION,sktdictdcs3.meanings,meghaduta1.POS,meghaduta1.GRAMMAR
FROM meghaduta1
INNER JOIN sktdictdcs3 ON meghaduta1.TEXT_UNIT='W' AND meghaduta1.WORD_NUMBER=sktdictdcs3.id

SELECT * FROM WordsAndMeanings
