from collections import defaultdict

DATA_DIR  = 'data/'
TEST = False
#Loaded files
filename = 'file'
if(TEST):
    filename = 'test'
f_en = open(DATA_DIR+filename +'.en', 'r')
f_de = open(DATA_DIR+filename+'.de', 'r')
f_align = open(DATA_DIR +filename+'.aligned', 'r')

#phrase is the phrase as a string
#alignment is a list of pairs as follow : [[0,0],[0,1],[1,2]] ...
#The idea of the algorithm is to check if each word alone can be a phrase and to extend those phrase to get all possible combination
def extractPhrases(sentence_src,sentence_tgt,alignments,words_src_given_tgt,words_tgt_given_src):
    words = sentence_src.split()
    words_tgt = sentence_tgt.split()

    currentPhrase = [] # The current small phrases that are being built
    currentBoxes = [] # The corresponding boxes to the current phrases

    allPhrases=[] # A small phrase is defined by a phrase in which if you remove a word, it will no longer be a phraser
    first_index=[] #keep track of the index of the first word of the currentPhrases
    all_phrases_tgt = [] # all phrases in the target side

    lexical_src_given_tgt = [] # lexical probability of source given target
    lexical_tgt_given_src = [] # lexical probability of target given source

    for word_ind in range(len(words)) :
        wordAlignments = findWordAlignments(word_ind,alignments)
        #Add a new box and a new phrase for the word aline
        currentBoxes.append([-1,-1,-1,-1])
        currentPhrase.append("")
        first_index.append(None)

        for i in range(len(currentBoxes)):
            if currentPhrase[i] == "":
                currentPhrase[i] = words[word_ind]
                first_index[i]=word_ind
            else:
                currentPhrase[i] += " " + words[word_ind]
            correct, newBox = checkCorrectPhrase(currentBoxes[i],wordAlignments,alignments)
            if correct :
                phrase_tgt = [None] * len(words_tgt)  # to generate phrase in the target side

                allPhrases.append(currentPhrase[i])
                target_index = []

                # getting the target side phrases
                for cpi in range(first_index[i],word_ind+1):
                    word_alignments = findWordAlignments(int(cpi),alignments)
                    for wa in word_alignments:
                        phrase_tgt[wa[1]] = words_tgt[wa[1]]
                        target_index.append(wa[1])

                phrase_tgt_new = " ".join([x for x in phrase_tgt if x != None])
                all_phrases_tgt.append(phrase_tgt_new)

                # getting the l(e|f) and l(f|e)
                lexval_temp = 1.0
                lexval_temp2 = 1.0
                #print(currentPhrase[i], phrase_tgt_new)
                for cpi in range(first_index[i],word_ind+1):
                    word_alignments = findWordAlignments(int(cpi),alignments)
                    temp = 0
                    if (len(word_alignments) > 0):
                        for wa in word_alignments:
                            temp += words_src_given_tgt[words[wa[0]]][words_tgt[wa[1]]]
                        temp /= len(word_alignments)
                        lexval_temp *= temp

                for ti in target_index:
                    word_alignments2 = findWordAlignments(int(ti),alignments, True)
                    temp2 = 0
                    if (len(word_alignments2) > 0):
                        for wa in word_alignments2:
                            temp2 += words_tgt_given_src[words_tgt[wa[1]]][words[wa[0]]]
                        temp2 /= len(word_alignments2)
                        lexval_temp2 *= temp2

                    # temp2 = 0
                    # for wa in word_alignments2:
                    #     temp2 += words_tgt_given_src[words_tgt[wa[1]]][words[wa[0]]]
                    # temp2 /= len(word_alignments2)
                    # lexval_temp2 *= temp2

                lexical_src_given_tgt.append(lexval_temp)
                lexical_tgt_given_src.append(lexval_temp2)
            currentBoxes[i] = newBox

    return allPhrases, all_phrases_tgt, lexical_src_given_tgt, lexical_tgt_given_src
#Check if a phrase is correct by looking if no words are aligned to the outside
#newWordIndex: index of the new word in the phrase
#alignement: list of pairs as follow : [[0,0],[0,1],[1,2]] ...
def checkCorrectPhrase(prevBox,wordAlignments,alignments):
    newBox = computePhraseBox(prevBox,wordAlignments)
    #test if there is no alignment of a word in the box (either en or de) to a word outside it
    #Maily, test if there is no alignement [x,y] such that x in the box but not y , or the opposite
    correct=True
    for pair in alignments :
        x_in_box = (newBox[0]<=pair[0]) and (pair[0]<=newBox[2])
        y_in_box = (newBox[1]<=pair[1]) and (pair[1]<=newBox[3])
        if( (x_in_box and not y_in_box) or (not x_in_box and y_in_box)):
            correct=False
            break
    return correct,newBox


#Given a word index, compute all the alignments from this word to other words. If reverse parameter is true, check the opposite alignments
#word_index: index of the word in the phrase
#alignments: list of pairs as follow : [[0,0],[0,1],[1,2]] ...
#reverse: if alignments is de -> en , set reverse to true to have the corresponding en -> de alignments
def findWordAlignments(word_index,alignments,reverse=False):
    allAlignments = []
    for pair in alignments:
        if( (not reverse and (word_index==pair[0])) or (reverse and (word_index==pair[1]) ) ):
            allAlignments.append(pair)
    return allAlignments

# Compute the box associated to the phrase. The computation is done by extending the box due to the addition of a word to the phrase.
#ie: box is [0,1,2,3] (alignments are within the points (0,1) and (2,3)) and we want to add a new word which has the following alignment:
#(2,4), the box will then be extended as [0,1,2,4]
# prevBox: index of the words in the phrase: This is my desk , "my desk" => [2,3],  [-1,-1,-1,-1] if none
# newAlignment: alignement corresponding to the new word in the format [x,y]
def computePhraseBox(prevBox, newAlignment):
    box=prevBox
    for pair in newAlignment:
        x=pair[0]
        y=pair[1]
        if(box[0]==-1):
            box= [x,y,x,y]
        else:
            if(box[0]>x):
                box[0]=x
            if (box[1] > y):
                box[1] = y
            if (box[2] < x):
                box[2] = x
            if (box[3] < y):
                box[3] = y
    return box

def writeResults(filename, phrases_src_given_tgt_counts, lexical_src_given_tgt, lexical_tgt_given_src ):
    f = open(filename, 'w')
    f.write("f ||| e ||| p(f|e) p(e|f) l(f|e) l(e|f) ||| freq(f) freq(e) freq(f, e)\n")
    for source_phrase, targetToCountDict in phrases_src_given_tgt_counts.items():
        freq_f = 0
        #print(str(source_phrase) +" "+ str(phrases_src_given_tgt_counts[source_phrase]))
        #Compute frequencies
        for key, value in phrases_src_given_tgt_counts[source_phrase].items():
            freq_f+=value
        for target_phrase, freq_fe in targetToCountDict.items():
            if(freq_fe >0):
                freq_e = 0
                for key, value in phrases_src_given_tgt_counts.items():
                    if phrases_src_given_tgt_counts[key][target_phrase]:
                        freq_e+=phrases_src_given_tgt_counts[key][target_phrase]
                lef = lexical_src_given_tgt[source_phrase][target_phrase]
                lfe = lexical_tgt_given_src[target_phrase][source_phrase]
                # f   |||e    |||p(f|e)      p(e|f) l(f|e) l(e|f) |||freq(f) freq(e) freq(f, e)
                f.write(str(source_phrase) \
                        +" ||| " + str(target_phrase)\
                        +" ||| "+str(freq_fe/freq_e)+ " "+str(freq_fe/freq_f) + " " + str(sum(lef) / float(len(lef))) + " " + str(sum(lfe) / float(len(lfe)))\
                        +" ||| "+ str(freq_f)+ " "+ str(freq_e)+ " "+ str(freq_fe)+"\n" )
    f.close()

sentence_src = 'De minister van buitenlandse zaken brengt een bezoek aan Nederland vandaag'
sentence_tgt = 'The Secretary of State visits The Netherlands today'
myalignements = [[0,0],[1,1],[2,2],[3,3],[4,3],[5,4],[6,4],[7,4],[8,4],[9,5],[9,6],[10,7]]
#print(extractPhrases(sentence_src,sentence_tgt,myalignements))

#Expect ['De', 'De minister', 'De minister van', 'De minister van buitenlandse zaken', 'De minister van buitenlandse zaken brengt een bezoek aan',
#  'De minister van buitenlandse zaken brengt een bezoek aan Nederland',
# 'De minister van buitenlandse zaken brengt een bezoek aan Nederland vandaag',
# 'minister', 'minister van', 'minister van buitenlandse zaken', 'minister van buitenlandse zaken brengt een bezoek aan',
# 'minister van buitenlandse zaken brengt een bezoek aan Nederland', 'minister van buitenlandse zaken brengt een bezoek aan Nederland vandaag',
# 'van', 'van buitenlandse zaken', 'van buitenlandse zaken brengt een bezoek aan', 'van buitenlandse zaken brengt een bezoek aan Nederland',
# 'van buitenlandse zaken brengt een bezoek aan Nederland vandaag', 'buitenlandse zaken', 'buitenlandse zaken brengt een bezoek aan',
# 'buitenlandse zaken brengt een bezoek aan Nederland', 'buitenlandse zaken brengt een bezoek aan Nederland vandaag', 'brengt een bezoek aan',
# 'brengt een bezoek aan Nederland', 'brengt een bezoek aan Nederland vandaag', 'Nederland', 'Nederland vandaag', 'vandaag']

### count word occurences ###
words_src_given_tgt_counts = defaultdict(lambda : defaultdict(float))
words_tgt_given_src_counts = defaultdict(lambda : defaultdict(float))
for sentence_en, sentence_de, line_aligned in zip(f_en, f_de, f_align):
    words_de = sentence_de.replace("\n", "").split()
    words_en = sentence_en.replace("\n", "").split()
    alignments = []
    alignments_temp = line_aligned.replace("\n","").split(" ")
    for al in alignments_temp:
        alignments.append(al.split("-"))
    alignments=[list(map(int,pair)) for pair in alignments]
    for alig in alignments:
        words_src_given_tgt_counts[words_de[alig[0]]][words_en[alig[1]]] += 1.0
        words_tgt_given_src_counts[words_en[alig[1]]][words_de[alig[0]]] += 1.0

def normalize(d, target=1.0):
   raw = sum(d.values())
   factor = target/raw
   return {key:value*factor for key,value in d.iteritems()}

for key in words_src_given_tgt_counts:
    words_src_given_tgt_counts[key] = normalize(words_src_given_tgt_counts[key])
for key in words_tgt_given_src_counts:
    words_tgt_given_src_counts[key] = normalize(words_tgt_given_src_counts[key])

#sentence_src = 'a b c' #mapped to a1 b1 c1 d1 as followed
#sentence_tgt = 'a1 b1 c1 a2'
#myalignements = [[0,0],[1,1],[2,2],[0,3]]
#print(words_src_given_tgt_prob)
#print(words_tgt_given_src_prob)
#print(extractPhrases(sentence_src,sentence_tgt,myalignements,words_src_given_tgt_prob,words_tgt_given_src_prob))

#test with today(beginning) and vandaag(end)
#Problem :      a1   b1   c1   a2
#            a  .              .
#            b       .
#            c           .
#Desired output : b, c, bc, abc

### Task 1, find the frequency of the phrases ###
phrases_src_given_tgt_counts = defaultdict(lambda : defaultdict(float))
lexical_src_given_tgt_prob = defaultdict(lambda : defaultdict(list))
lexical_tgt_given_src_prob = defaultdict(lambda : defaultdict(list))
#TODO: also delete ?
#phrases_tgt_given_src_counts = defaultdict(lambda : defaultdict(float))
#TODO: delete ?
#phrases_src_counts = defaultdict(float)
#phrases_tgt_counts = defaultdict(float)

f_en = open(DATA_DIR+filename +'.en', 'r')
f_de = open(DATA_DIR+filename+'.de', 'r')
f_align = open(DATA_DIR +filename+'.aligned', 'r')

count = 0
for sentence_en, sentence_de, line_aligned in zip(f_en, f_de, f_align):
    if count%1000 == 0:
        print('count: '+ str(count))
    alignments = []
    alignments_temp = line_aligned.replace("\n","").split(" ")
    for al in alignments_temp:
        alignments.append(al.split("-"))
    alignments=[list(map(int,pair)) for pair in alignments]
    ### extract phrases and count phrases occurences ###
    phrases_src, phrases_tgt, lexical_src_given_tgt, lexical_tgt_given_src = extractPhrases(sentence_de.replace("\n",""), sentence_en.replace("\n",""), alignments, words_src_given_tgt_counts, words_tgt_given_src_counts)
    for p_src, p_tgt, l_src_tgt, l_tgt_src in zip(phrases_src, phrases_tgt, lexical_src_given_tgt, lexical_tgt_given_src):
        phrases_src_given_tgt_counts[p_src][p_tgt] += 1.0
        lexical_src_given_tgt_prob[p_src][p_tgt].append(l_src_tgt)
        lexical_tgt_given_src_prob[p_tgt][p_src].append(l_tgt_src)
        #phrases_tgt_given_src_counts[p_tgt][p_src] += 1.0
        #phrases_tgt_counts[p_tgt] += 1.0
        #phrases_src_counts[p_src] += 1.0
    count+=1

#TODO: simplify above code by removing variables and defining a main
writeResults("test_big.txt", phrases_src_given_tgt_counts, lexical_src_given_tgt_prob, lexical_tgt_given_src_prob)
#print(words_src_given_tgt_prob)
print('done')