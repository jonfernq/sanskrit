import re, sys, os
from tabulate import tabulate

# noun_paradigm_csv_to_flashcard.py

# reformats csv with flashcards for noun paradigms 
# into word meaning pairs for flashcards and grammatical paradigm tables
# to be written out to individual csv files, plain text files or 
# reformatted into javascript flip card flashcards
# for use in reveal.js or HP5, for instance

paradigm_pattern_html = """
            <section><small>
			<table><tbody>
			  <tr>
				<td class="gender"></td>
				<th scope="col">sing.</th>
				<th scope="col">du.</th>
				<th scope="col">pl.</th>
			  </tr>
			  <tr>
				<th scope="row" class="sh" data-c="1">nom.</th>
				<td class="t-deva" data-cn="1-1">{}</td>
				<td class="t-deva s1" data-cn="1-2">{}</td>
				<td class="t-deva s5" data-cn="1-3">{}</td>
			  </tr>
			  <tr>
				<th scope="row" class="sh" data-c="2">acc.</th>
				<td class="t-deva" data-cn="2-1">{}</td>
				<td class="t-deva s1" data-cn="2-2">{}</td>
				<td class="t-deva" data-cn="2-3">{}</td>
			  </tr>
			  <tr>
				<th scope="row" class="sh" data-c="3">instr.</th>
				<td class="t-deva" data-cn="3-1">{}</td>
				<td class="t-deva s2" data-cn="3-2">{}</td>
				<td class="t-deva" data-cn="3-3">{}</td>
			  </tr>
			  <tr>
				<th scope="row" class="sh" data-c="4">dat.</th>
				<td class="t-deva" data-cn="4-1">{}</td>
				<td class="t-deva s2" data-cn="4-2">{}</td>
				<td class="t-deva s3" data-cn="4-3">{}</td>
			  </tr>
			  <tr>
				<th scope="row" class="sh" data-c="5">abl.</th>
				<td class="t-deva" data-cn="5-1">{}</td>
				<td class="t-deva s2" data-cn="5-2">{}</td>
				<td class="t-deva s3" data-cn="5-3">{}</td>
			  </tr>
			  <tr>
				<th scope="row" class="sh" data-c="6">gen.</th>
				<td class="t-deva" data-cn="6-1">{}</td>
				<td class="t-deva s4" data-cn="6-2">{}</td>
				<td class="t-deva" data-cn="6-3">{}</td>
			  </tr>
			  <tr>
				<th scope="row" class="sh" data-c="7">loc.</th>
				<td class="t-deva" data-cn="7-1">{}</td>
				<td class="t-deva s4" data-cn="7-2">{}</td>
				<td class="t-deva" data-cn="7-3">{}</td>
			  </tr>
			  <tr>
				<th scope="row" class="sh" data-c="8">voc.</th>
				<td class="t-deva" data-cn="8-1">{}</td>
				<td class="t-deva s1" data-cn="8-2">{}</td>
				<td class="t-deva s5" data-cn="8-3">{}</td>
			  </tr>
			</tbody></table>
            </small></section>
"""

def expand_multiple_paradigms(x):
    r1 = re.findall(r"^(\w+)\/(\w+)\,(.+)$",x)
    if r1:
        a = r1[0][0] + ', ' + r1[0][2]
        b = r1[0][1] + ', ' + r1[0][2]
        return [a,b]
    else:
        r2 = re.findall(r"^(\w+)\,(.+)$",x)
        a = r2[0][0] + ', ' + r2[0][1]
        return [a] 

def make_noun_flashcards(infile, outfile):
    infile = open (infile, "r", encoding='utf8')
    in_lines = infile.readlines() 
    infile.close()

    paradigm = []
    for l in in_lines:
        paradigm.append(l.rstrip().split(','))

    # rearrange paradigm into flashcard question-answer pairs
    big = []
    for i in range(1,7): 
        sg = paradigm[i][1] + ', ' + paradigm[i][0] + ' ' + paradigm[0][1]
        du = paradigm[i][2] + ', ' + paradigm[i][0] + ' ' + paradigm[0][2]
        pl = paradigm[i][3] + ', ' + paradigm[i][0] + ' ' + paradigm[0][3]
        big.append(expand_multiple_paradigms(sg))
        big.append(expand_multiple_paradigms(du))
        big.append(expand_multiple_paradigms(pl))

    flat_list = [item for l in big for item in l]

    # write the csv flashcard question-answer pairs to a file for use in flashcard system 
    fileout = open(outfile,'w', encoding='utf8')
    for j in flat_list:
        fileout.write(j)
        fileout.write('\n')
    fileout.close()

def convert_dict_values_from_list_to_string(dict):
    d = {}   
    for k in dict: 
        d[k] = ', '.join(dict[k])
    return d

def paradigm_to_flashcard_dictionary(words,grammar): 
    # accumulate grammatical functions for each word through insertion into dictionary 
    fcards = {}  
    for i in range(0,len(words)): 
        if i < len(grammar): 
            if words[i] in fcards:
                # add grammar to existing value in the dictionary which is a list 
                fcards[words[i]].append(grammar[i]) 
            else: 
                # add new key-value to dictionary with value being list of grammatical functions for the word 
                fcards[words[i]] = [grammar[i]] 
        else: 
            print('ERROR: grammatical function missing for ', words[i], ' index: ', i)
    fcards2 = convert_dict_values_from_list_to_string(fcards)
    return fcards2

def paradigm_to_paradigm_dictionary(words,grammar):  
    fcards = {}  
    for i in range(0,len(words)): 
        if i < len(grammar):  
                fcards[grammar[i]] = words[i] 
        else: 
            print('ERROR: grammatical function missing for ', words[i], ' index: ', i)
    return fcards

def make_fcard_file(fcard_set):
    file_string = "" 
    for f in fcard_set:
        file_string = file_string + f + '\t' + fcard_set[f] + '\n' 
    return file_string 

def get_grammar_and_paradigms(infile): 
    infile = open (infile, "r", encoding='utf8')
    in_lines = infile.readlines() 
    infile.close()
    # create list of dictionaries of flashcards, one per paradigm
    grammar = in_lines[0].replace(' ', '').strip().split(',')
    del grammar[0] 
    paradigms = in_lines[1:]
    return grammar, paradigms

def get_name_and_words(paradigm):
    # get name of paradigms and word array for paradigm 
    p = paradigm.replace(' ', '').strip().split(',')
    name = p[0]
    words = p[1:]
    return name, words

def noun_paradigms_file_to_flashcards(infile): 
    # make flashcard set dictionaries for all paradigms 
    (grammar, paradigms) = get_grammar_and_paradigms(infile)
    fcard_sets = {}
    for p in paradigms: 
        (name, words) = get_name_and_words(p)
        fcard_sets[name] = paradigm_to_flashcard_dictionary(words,grammar) 
    return fcard_sets

def noun_paradigms_file_to_paradigms(infile): 
    # make flashcard set dictionaries for all paradigms 
    (grammar, paradigms) = get_grammar_and_paradigms(infile)
    paradigm_sets = {}
    for p in paradigms: 
        (name, words) = get_name_and_words(p)
        paradigm_sets[name] = paradigm_to_paradigm_dictionary(words,grammar) 
    return paradigm_sets

    # iterate through Skt words entering into dictionary 
    # accumulating in the value the multiple gram functions 
    # associated with the skt word 

def make_noun_paradigm_flashcard_html(infile): 
    pass 
    return np_html

def write_flashcards(fcard_sets):
    for f in fcard_sets:
        out_file = f + ".txt"
        file_string = make_fcard_file(fcard_sets[f])
        print(out_file, ': ', fcard_sets[f], '\n')
        fileout = open(out_file,'w', encoding='utf8')
        fileout.write("%s" % (file_string))
        fileout.close()

def write_html(html_string): 
    pass

def write_flashcards_to_plaintext_table(fcard_sets):
    original_stdout = sys.stdout
    with open('fcard_sets.txt', 'w', encoding='utf8') as f:
        sys.stdout = f 
        for name in fcard_sets:
            print('NAME: ', name)
            l = tabulate(list(fcard_sets[name].items()))
            print(l, '\n') 
        sys.stdout = original_stdout 

def write_paradigms_to_plaintext_table(paradigm_sets):
    #print(paradigm_sets)
    #quit() 
    paradigm_pattern = "\tSing.\tDual.\tPlur.\n" + \
    "Nom:\t{}\t{}\t{}\n" + \
    "Acc:\t{}\t{}\t{}\n" + \
    "Instr:\t{}\t{}\t{}\n" + \
    "Dat:\t{}\t{}\t{}\n" + \
    "Abl:\t{}\t{}\t{}\n" + \
    "Gen:\t{}\t{}\t{}\n" + \
    "Loc:\t{}\t{}\t{}\n" + \
    "Voc:\t{}\t{}\t{}\n" 
    p_tables = ""
    for name in paradigm_sets:
        #for name in p:
        paradigm = paradigm_sets[name]
        #print('NAME:', name)
        #print('PARADIGM:', paradigm)
        #quit() 
        p = paradigm_pattern.format(paradigm['Nom.Sing.'], paradigm['Nom.Dual'], paradigm['Nom.Plur.'], \
            paradigm['Acc.Sing.'], paradigm['Acc.Dual'], paradigm['Acc.Plur.'], \
            paradigm['Inst.Sing.'], paradigm['Inst.Dual'], paradigm['Inst.Plur.'], \
            paradigm['Dat.Sing.'], paradigm['Dat.Dual'], paradigm['Dat.Plur.'], \
            paradigm['Abl.Sing.'], paradigm['Abl.Dual'], paradigm['Abl.Plur.'], \
            paradigm['Gen.Sing.'], paradigm['Gen.Dual'], paradigm['Gen.Plur.'], \
            paradigm['Loc.Sing.'], paradigm['Loc.Dual'], paradigm['Loc.Plur.'], \
            paradigm['Voc.Sing.'], paradigm['Voc.Dual'], paradigm['Voc.Plur.'])
        p_tables = p_tables + name + "\n\n" + p.expandtabs(14) + "\n\n"
    fileout = open("noun_paradigms.txt",'w', encoding='utf8')
    fileout.write("%s" % (p_tables))
    fileout.close()

def paradigm_and_fcard_html(name, paradigm, fcards):
    # write out reveal.js html page for aall noun paradigms 
    # with one page per paradigm with vertical branch for flashcards associated with noun paradigm
    # expand paradigm into the super structure
    # and each flashcard into sub structures
    print("NAME:", name)
    print("PARADIGM: ", paradigm)
    print("FCARDS:", fcards)

    html_for_paradigm = "" 
    table = paradigm_pattern_html.format(paradigm['Nom.Sing.'], paradigm['Nom.Dual'], paradigm['Nom.Plur.'], \
        paradigm['Acc.Sing.'], paradigm['Acc.Dual'], paradigm['Acc.Plur.'], \
        paradigm['Inst.Sing.'], paradigm['Inst.Dual'], paradigm['Inst.Plur.'], \
        paradigm['Dat.Sing.'], paradigm['Dat.Dual'], paradigm['Dat.Plur.'], \
        paradigm['Abl.Sing.'], paradigm['Abl.Dual'], paradigm['Abl.Plur.'], \
        paradigm['Gen.Sing.'], paradigm['Gen.Dual'], paradigm['Gen.Plur.'], \
        paradigm['Loc.Sing.'], paradigm['Loc.Dual'], paradigm['Loc.Plur.'], \
        paradigm['Voc.Sing.'], paradigm['Voc.Dual'], paradigm['Voc.Plur.'])
    card_for_paradigm = """
        <section>
        <div class="maincontainer">
            <div class="thecard">
                <div class="thefront"><center><p>{}</p></center></div>
                <div class="theback"><center><p>{}</p></center></div>
            </div>
        </div>
        </section>  
    """ 
    cards = ""
    for p in paradigm: 
        c = card_for_paradigm.format(paradigm[p], p)
        cards = cards + c 
    html_for_paradigm = "<section>" + "<h3>"+ name + "</h3>" + table + cards + "</section>"
    #print('HTML FOR PARADIGM:', html_for_paradigm)
    #quit()  
    return html_for_paradigm

def write_revealjs_paradigm_flashcard_html(paradigm_sets,fcard_sets):
        # format grammatical paradigms and flashcards for reveal.js presentation of a single paradigm
        f = "" 
        for name in paradigm_sets:
            paradigm = paradigm_sets[name]
            fcards   = fcard_sets[name]
            f = f + paradigm_and_fcard_html(name, paradigm, fcards)
        fileout = open("noun_paradigms_reveal.txt",'w', encoding='utf8')
        fileout.write("%s" % (f))
        fileout.close()

        with open('reveal_template_top.txt', 'r') as file:
            top = file.read()
        with open('reveal_template_bottom.txt', 'r') as file:
            bottom = file.read()
        pg = top + f + bottom 

        os.chdir("C:\\JAVASCRIPT\\reveal.js-master")
        fileout = open("noun_paradigms_reveal.html",'w', encoding='utf8')
        fileout.write("%s" % (pg))
        fileout.close()

def main():
    infile = "C:\\PYTHON\\FORMAT_FLASHCARDS\\noun_paradigms.csv" 
    fcard_sets = noun_paradigms_file_to_flashcards(infile)
    print(fcard_sets)
    write_flashcards_to_plaintext_table(fcard_sets)
    write_flashcards(fcard_sets)
    paradigm_sets = noun_paradigms_file_to_paradigms(infile)
    write_paradigms_to_plaintext_table(paradigm_sets)
    write_revealjs_paradigm_flashcard_html(paradigm_sets,fcard_sets)
    quit() 

    for np in np_lst: 
        np_html = make_noun_paradigm_flashcard_html(np)
        write_html(np_html)


if __name__ == '__main__':
    main()







