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
def extractPhrases(sentence_src,sentence_tgt,alignments):
    words = sentence_src.split()
    words_tgt = sentence_tgt.split()

    currentPhrase = [] # The current small phrases that are being built
    currentBoxes = [] # The corresponding boxes to the current phrases

    allPhrases=[] # A small phrase is defined by a phrase in which if you remove a word, it will no longer be a phraser
    first_index=[] #keep track of the index of the first word of the currentPhrases
    all_phrases_tgt = [] # all phrases in the target side


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

                # getting the target side phrases
                for cpi in range(first_index[i],word_ind+1):
                    word_alignments = findWordAlignments(int(cpi),alignments)
                    for wa in word_alignments:
                        phrase_tgt[wa[1]] = words_tgt[wa[1]]
                all_phrases_tgt.append(" ".join([x for x in phrase_tgt if x != None]))
            currentBoxes[i] = newBox

    return allPhrases, all_phrases_tgt
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

sentence_src = 'a b c' #mapped to a1 b1 c1 d1 as followed
sentence_tgt = 'a1 b1 c1 a2'
myalignements = [[0,0],[1,1],[2,2],[0,3]]
#print(extractPhrases(sentence_src,sentence_tgt,myalignements))

#test with today(beginning) and vandaag(end)
#Problem :      a1   b1   c1   a2
#            a  .              .
#            b       .
#            c           .
#Desired output : b, c, bc, abc


### Task 1, find the frequency of the phrases ###
phrases_src_given_tgt_counts = defaultdict(lambda : defaultdict(float))
phrases_tgt_given_src_counts = defaultdict(lambda : defaultdict(float))
phrases_src_counts = defaultdict(float)
phrases_tgt_counts = defaultdict(float)

count = 0
for sentence_en, sentence_de, line_aligned in zip(f_en, f_de, f_align):
    if count%1000 == 0:
        print('count: '+ str(count))
    alignments = []
    alignments_temp = line_aligned.replace("\n","").split(" ")
    for al in alignments_temp:
        alignments.append(al.split("-"))
    alignments=[list(map(int,pair)) for pair in alignments]
    phrases_src, phrases_tgt = extractPhrases(sentence_de.replace("\n",""), sentence_en.replace("\n",""), alignments)
    for p_src, p_tgt in zip(phrases_src, phrases_tgt):
        phrases_src_given_tgt_counts[p_src][p_tgt] += 1.0
        phrases_tgt_given_src_counts[p_tgt][p_src] += 1.0
        phrases_tgt_counts[p_tgt] += 1.0
        phrases_src_counts[p_src] += 1.0
    count+=1

### Task 2, find p(f|e) and p(e|f)
pfe = defaultdict(lambda : defaultdict(float))
pef = defaultdict(lambda : defaultdict(float))
# p(e|f)
for key in phrases_src_given_tgt_counts:
    for key2 in phrases_src_given_tgt_counts[key]:
        pef[key][key2] = phrases_src_given_tgt_counts[key][key2] / phrases_src_counts[key]
# p(f|e)
for key in phrases_tgt_given_src_counts:
    for key2 in phrases_tgt_given_src_counts[key]:
        pef[key][key2] = phrases_tgt_given_src_counts[key][key2] / phrases_tgt_counts[key]

print('done')