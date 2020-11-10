import re, os, sys, sqlite3
from sqlite3 import Error
from tabulate import tabulate

# Script: extract_interlinear.py

# This script formats an interlinear translation from
# data in the Digital Corpus of Sanskrit (DCS).
# First, lines of Sanskrit text and translations 
# are taken from an Sqlite database (used for instance
# to reformat DCS lexical info into flashcards).
# Then the DCS words for the Sanskrit line are taken
# from the database and inverted or transposed into
# an interlinear translation in plain text and html.   


# open sqlite database 
def create_connection_cursor(db_file):
    # open database and establish cursor 
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
    except Error as e:
        print(e)
        quit() 
    return cur

def write_utf8(out_file, out_txt):
    f = open(out_file, 'w', encoding='utf8')
    f.write(out_txt)
    f.close() 

def transpose(x):
    #test case: z = transpose([[1,2,3],[4,5,6],[7,8,9]])
    #print('transpose:', x)
    return list(map(lambda *a: list(a), *x))

def flatten(l): 
    #test case: print(flatten([1,[2,3],4]))
    return flatten(l[0]) + (flatten(l[1:]) if len(l) > 1 else []) if type(l) is list else [l]

def tag(l):
    # test case: tag([['1','2','3'],['4','5','6'],['7','8','9']])
    return list(map(lambda y: ['<tr>'] + list(map(lambda x: '<td>' + x + '</td>', y)) + ['</tr>\n'], l))

top = """
<html>
<head>
<style>
  table {
    border-collapse: collapse;
  }
  th, td {
    border: 1px solid orange;
    padding: 10px;
    text-align: left;
  }
</style>
</head>
<body>
"""

end_page = "</html>"

class Interlinear_Line():
# one line with words glossed underneath
    def __init__(self, wrk, ch, verse, half_verse, txt, words):
        self.wrk   = wrk
        self.ch    = ch
        self.verse = verse
        self.half_verse = half_verse
        self.txt        = txt
        self.words      = words

    def __str__(self):
        return 'LINE:({},{},{},{},{})'.format(self.wrk, self.ch, self.verse, self.half_verse, self.txt)

    def __repr__(self):
        return self.__str__()

class Interlinear_Text():
# collection of interlinear lines
    def __init__(self, wrk, ch, db):
        self.wrk = wrk
        self.ch  = ch
        self.db  = db
        self.lines = []
        self.display_lines = []  
        self.cur = create_connection_cursor(self.db)
        self.__create_lines()
        self.__display_lines()

        #self.__print_display_lines()
        #quit() 

        #self.words = get_words_for_line(cur, tbl, txt, ch, verse, half_verse)
        #self.display_lines = compose_interlinear_by_line(cur, wrk, line_records)

    def __str__(self):
        #return('\n'.join(self.lines))
        return '({})'.format(self.lines)

    def __repr__(self):
        return self.__str__()

    def __create_lines(self):
        # sql query retrieving all text line 'L' records in db    
        l = "SELECT CHAPTER, VERSE, HALF_VERSE, SENTENCE_COMPOUND_WORD FROM {0} WHERE TEXT_UNIT = 'L'".format(self.wrk)
        self.cur.execute(l)
        line_records = list(self.cur.fetchall())
        for l in line_records:
            (ch, verse, half_verse, txt) = l 
            # sql query retrieving words for one line (half-verse)  
            wrdsql = "SELECT WORD_CITATION, SENTENCE_COMPOUND_WORD, GRAMMAR, MEANING \
                    FROM {0} WHERE CHAPTER='{1}' AND VERSE='{2}' AND HALF_VERSE='{3}' \
                    AND TEXT_UNIT = 'W' ".format(self.wrk, ch, verse, half_verse)
            self.cur.execute(wrdsql)
            word_records = list(self.cur.fetchall())
            words = list(map(lambda x: list(x), word_records))
            self.lines.append(Interlinear_Line(self.wrk, ch, verse, half_verse, txt, words))


    def __display_lines(self):
        #column_headings = ['STEM:','INFL:','GRAM:'] # 'STEM:' 'INFL:' 'GRAM:'
        for l in self.lines:
            if not l.words:
                continue 
            # flip word glosses giving vertically inflected form, stem form, grammatical function
            t = transpose(l.words)
            interlinear = [t[0]] + [t[1]] + [t[2]]
            # make separate wordlist under interlinear array (because definitions too long)
            wl = [t[0]] + [t[3]]
            wordlist = transpose(wl)
            interlinear[0].insert(0, 'STEM:')
            interlinear[1].insert(0, 'INFL:')
            interlinear[2].insert(0, 'GRAM:')
            self.display_lines.append([l.wrk,l.ch,l.verse,l.half_verse,l.txt,interlinear,wordlist])

    def __print_display_lines(self):
        for l in self.display_lines:
            print(l[0:5],'\n')
            for i in l[5]:
                print(i, '\n')
            print('\n')

    def interlinear_plaintext(self):
        #self.display_lines[5].append('STEM:')
        #self.__print_display_lines()
        #quit() 

        mid = "" 
        # display_lines = [...[interlinear, wordlist] ...]
        for l in self.display_lines:
            (wrk, ch, verse, half_verse, txt, interlinear, wordlist) = l 
            title = wrk + ' ' + ch + '.' + str("{:02d}".format(int(verse))) + '.' + half_verse 
            heading = "\n{}\n{}\n{}\n".format(title, txt, "")
            mid1 = tabulate(interlinear) 
            mid2 = ''.join(map(lambda x: ' - '.join(x) + '\n', wordlist)) + '\n'
            mid = mid + heading + mid1 + '\n' + 'VOCABULARY:\n' + mid2 + '\n'
        pg = mid 
        return pg

    def interlinear_html(self):
        self.__display_lines()
        mid = "" 
        # display_lines = [...[interlinear, wordlist] ...]
        for l in self.display_lines:
            (wrk, ch, verse, half_verse, txt, interlinear, wordlist) = l 
            title = wrk + ' ' + ch + '.' + str("{:02d}".format(int(verse))) + '.' + half_verse 
            heading = "<h1>{}</h1>\n<center><h2>{}</h2></center><p>{}</p>\n\n<table>".format(title, txt, "")
            mid1 = ''.join(flatten(tag(interlinear))) 
            mid2 = '<ul>' + ''.join(map(lambda x: '<li>' + ' - '.join(x) + '</li>', wordlist)) + '</ul>' 
            mid = mid + '\n' + '<section>' + '\n' + heading + mid1 + '\n' + mid2 + '\n' + '</section>' + '\n' 
            pg = top + mid + end_page
        return pg


# +++++++++++++++++++++++++++
# MAIN PROCESSING BEGINS HERE:  
#  INTERLINEAR TRANSLATION

def main():

    il = Interlinear_Text('kumarasambhava_1', '1', r"C:\sqlite\db\sanskritDB.db")
    pg = il.interlinear_plaintext()
    write_utf8("kumara_interlinear_1.txt", pg)
    pg_html = il.interlinear_html()
    write_utf8("kumara_interlinear_1.html", pg_html)

if __name__ == '__main__':
    main()

