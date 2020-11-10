import re, os, sys, pickle

# Script: dcs_reformat_into_csv.py

# This code is to run on Digital Corpus of Sanskrit (DCS) files 
# to reform them into CSV files loadable into a spreadsheet 
# or Sqlite relational database that provide a starting point for
# working in interlinear translations.   
# The structural parts of these files correspond to: 
# 1. works, 2. chapters, 3. lines/stanzas, 4. half-lines, 4. compounds, and 5. words.  

replacements = {
    "Number=1" : "s",
    "Number=2" : "d",
    "Number=3" : "p",
    "Gender=Masc" : "m",
    "Gender=Neut" : "n",
    "Gender=Fem"  : "f",
    "Gender="  : "?",
    "Person=1" : "1",
    "Person=2" : "2",
    "Person=3" : "3",
    "Number=Sing"  : "s",
    "Number=Plur" : "p",
    "Case=Cpd" : "Comp.",
    "VerbForm=Abs" : "Abs.",
    "VerbForm=Inf" : "Inf.",
    "Tense=Pres|Mood=Ind|Voice=Pass|" : "Pass|",
    "Tense=Fut|Mood=Ind|" : "Fut|",
    "Tense=Pres|Mood=Ind|" : "Pres|",  
    "Tense=Pres|Mood=Imp|" : "Imp|",
    "Tense=Impf|Mood=Ind|" : "Impf|",
    "Tense=Pres|Mood=Opt|" : "Opt|",
    "Tense=Perf|Mood=Ind|" : "Perf|",
    "Tense=Aor|Mood="  : "Aor|",
    "|VerbForm=PPP" : "|PPP",
    "|VerbForm=PPA" : "|PPA",
    "|Tense=Pres|Voice=Pass|VerbForm=Part" : "|PresPassPart",
    "|Tense=Pres|VerbForm=Part" : "|PresPart",
    "Formation=" : "",
    "Case=" : "",
  } 

def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 

def get_list_of_files(database_dir):
    CURR_DIR = os.getcwd()
    os.chdir(database_dir)
    print("DIR CHANGED")
    files_path = [os.path.abspath(x) for x in os.listdir()]
    os.chdir(CURR_DIR)
    return files_path

def make_line_record(work, chapter, line, half_line, text_line):
    line_list = ['L', work, chapter, line, half_line, '', text_line]
    line_string = ','.join(line_list)
    return line_string

def is_word_record(line):
    if re.match(r"^\d+\t", line):
        return True
    else: 
        return False

def make_word_record(work, chapter, line, half_line, item):
    item = item + '\n'
    item_list = item.strip().split('\t')

    # change grammatical paradigm to make simpler and easy to read
    item_list[5] = multiple_replace(replacements, item_list[5])

    # add word definition to record
    word = item_list[10].strip()

    word_list = ['W', work, chapter, line, half_line] + item_list
    word_string = ','.join(word_list)
    return word_string
    
def is_compound_record(line):
    # check if number-dash_number followed by tab
    return re.match(r"^\d+-\d+\t", line)

def make_compound_record(work, chapter, line, half_line, item):
    item = item + '\n'
    item_list = item.strip().split('\t')
    compound_list = ['C', work, chapter, line, half_line] + item_list
    compound_string = ','.join(compound_list)
    return compound_string

def trim_space(list):
    new_list = []
    for item in list:
        if len(item) > 0:
            new_list.append(item)
    return new_list

def ParseChapterFile(in_path):
    # Get list of all lines in sarga file
    fileHandler = open (in_path, "r", encoding='utf8')
    listOfLines = fileHandler.readlines() 
    fileHandler.close()

    # strip off header info on text
    # get header info for whole sarga 
    work         = listOfLines[0][9:].strip()
    text_id      = listOfLines[1][12:].strip()    ## text_id: 405
    chapter_full = listOfLines[2][12:].strip()    ## chapter: BKŚS, 8
    chapter_id   = listOfLines[3][15:].strip()    ## chapter_id: 7513
    blankline    = listOfLines[4].strip()

    # ## chapter: MBh, 1, 71
    # ## chapter: BKŚS, 8
    chapter_list = chapter_full.split(',')
    work2 = chapter_list[0].strip()

    print('CHAPTER_LIST:', chapter_list)

    if len(chapter_list) < 2:
        print('ERROR: Chapter information missing')
        quit()

    if len(chapter_list) == 3:
        #print('CHAPTER_LIST1:', len(chapter_list), chapter_list)
        chapter = chapter_list[1].strip() + '.' + chapter_list[2].strip()
    else:
        #print('CHAPTER_LIST2:', len(chapter_list), chapter_list)
        chapter = chapter_list[1].strip()

    # remove header info 
    del(listOfLines[0:5])

    # reduce remainder to string,  
    stringOfLines = ''.join(listOfLines) 

    # check string version of file, if not "\n\n" at end of file then add 
    # (this is needed because last chunk in DCS files ends differently in "\n")
    # if not end of string is "\n\n" then if "\n" add "\n" else add "\n"

    # parse out blankline-separated chunk for each sloka line
    chunks = re.findall(r"(.+?\n\n)", stringOfLines, re.MULTILINE | re.DOTALL)

    # isolated chunks of sloka lines to file
    chunks_string = ''.join(chunks)
    with open("output.txt",'w', encoding='utf8') as result:
         result.write(chunks_string)

    #fileout = open(out_path,'w', encoding='utf8')
    out_records = []

    # chunked sloka lines in list of lists
    if chunks:
        for chunk in chunks:
            chunk_list = chunk.split('\n')

            # get header info for whole sarga 
            line      = chunk_list[2][21:].strip() # text_line_counter  
            half_line = chunk_list[3][24:].strip() # text_line_subcounter
            text_line = chunk_list[0][13:].strip() # text_line 

            line_record = make_line_record(work, chapter, line, half_line, text_line)
            out_records.append(line_record)

            del chunk_list[0:4]
            chunk_list2 = trim_space(chunk_list)

            print('line:', work, chapter, line, half_line)

            for item in chunk_list2:
                if is_word_record(item): 
                    word_record = make_word_record(work, chapter, line, half_line, item)
                    out_records.append(word_record)
                elif is_compound_record(item):
                    compound_record = make_compound_record(work, chapter, line, half_line, item)
                    out_records.append(compound_record)
                else: 
                    print('ERROR: DCS file line neither word or compound:' + item)
    return out_records
  


# MAIN PROCESSING

os.chdir("C:\\PYTHON\\KUMARASAMBHAVA")
files_list = ["C:\\PYTHON\\KUMARASAMBHAVA\\Kumārasaṃbhava-DCS-1.txt","C:\\PYTHON\\KUMARASAMBHAVA\\Kumārasaṃbhava-DCS-2.txt"]
out_file = "C:\\PYTHON\\KUMARASAMBHAVA\\kumarasambhava_1_2.csv"

# input: files_list, outfile
out_records = ["TEXT_UNIT,WORK,CHAPTER,VERSE,HALF_VERSE,WORD,SENTENCE_COMPOUND_WORD,WORD_CITATION,MEANING,POS,GRAMMAR,BL2,BL3,BL4,BL5,WORD_NUMBER,BL6,BL7"]
i = 0 
# read records from all DCS files into lists for massive CSV file
for in_path in files_list:
    sarga_records = ParseChapterFile(in_path)
    print(len(sarga_records))
    out_records.extend(sarga_records)
    i = i + 1 
print(i)

# make strings from lists and write out to massive CSV file
file_string = '\n'.join(out_records) 
fileout = open(out_file,'w', encoding='utf8')
fileout.write("%s" % (file_string))
fileout.close()
