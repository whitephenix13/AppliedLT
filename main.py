DATA_DIR  = 'data/'

#Loaded files
f_en = open(DATA_DIR+'file.en', 'r')
f_de = open(DATA_DIR+'file.de', 'r')
f_align = open(DATA_DIR + 'file.aligned', 'r')

#phrase is the phrase as a string
#alignment is a list of pairs as follow : [[0,0],[0,1],[1,2]] ...
#The idea of the algorithm is to check if each word alone can be a phrase and to extend those phrase to get all possible combination
def extractPhrases(phrase,alignments):
    words = phrase.split()
    currentPhrase = [] # The current small phrases that are being built
    currentBoxes = [] # The corresponding boxes to the current phrases

    allPhrases=[] # A small phrase is defined by a phrase in which if you remove a word, it will no longer be a phrase
    for word_ind in range(len(words)) :
        wordAlignments = findWordAlignments(word_ind,alignments)
        #Add a new box and a new phrase for the word aline
        currentBoxes.append([-1,-1,-1,-1])
        currentPhrase.append("")
        for i in range(len(currentBoxes)):
            if currentPhrase[i] == "":
                currentPhrase[i] = words[word_ind]
            else:
                currentPhrase[i] += " " + words[word_ind]

            correct, newBox = checkCorrectPhrase(currentBoxes[i],word_ind,wordAlignments)
            if correct :
                allPhrases.append(currentPhrase[i])
            currentBoxes[i]= newBox

    return allPhrases
#Check if a phrase is correct by looking if no words are aligned to the outside
#newWordIndex: index of the new word in the phrase
#alignement: list of pairs as follow : [[0,0],[0,1],[1,2]] ...
def checkCorrectPhrase(prevBox,newWordIndex,wordAlignments):
    newBox= computePhraseBox(prevBox,wordAlignments)
    #test if there is no alignment of a word in the box (either en or de) to a word outside it
    #Maily, test if there is no alignement [x,y] such that x in the box but not y , or the opposite
    correct=True
    for pair in alignements :
        x_in_box = (newBox[0]<=pair[0]) and (pair[0]<=newBox[2])
        y_in_box = (newBox[1]<=pair[1]) and (pair[1]<=newBox[3])
        if( (x_in_box and not y_in_box) or (not x_in_box and y_in_box)):
            correct=False
            break
    return correct,newBox


#Given a word index, compute all the alignments from this word to other words. If reverse parameter is true, check the opposite alignments
#word_index: index of the word in the phrase
#alignements: list of pairs as follow : [[0,0],[0,1],[1,2]] ...
#reverse: if alignments is de -> en , set reverse to true to have the corresponding en -> de alignements
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


phrase = 'De minister van buitenlandse zaken brengt een bezoek aan Nederland vandaag'
alignements = [[0,0],[1,1],[2,2],[3,3],[4,3],[5,4],[6,4],[7,4],[8,4],[9,5],[9,6],[10,7]]
print(extractPhrases(phrase,alignements))
#Expect ['De', 'De minister', 'De minister van', 'De minister van buitenlandse zaken', 'De minister van buitenlandse zaken brengt een bezoek aan',
#  'De minister van buitenlandse zaken brengt een bezoek aan Nederland',
# 'De minister van buitenlandse zaken brengt een bezoek aan Nederland vandaag',
# 'minister', 'minister van', 'minister van buitenlandse zaken', 'minister van buitenlandse zaken brengt een bezoek aan',
# 'minister van buitenlandse zaken brengt een bezoek aan Nederland', 'minister van buitenlandse zaken brengt een bezoek aan Nederland vandaag',
# 'van', 'van buitenlandse zaken', 'van buitenlandse zaken brengt een bezoek aan', 'van buitenlandse zaken brengt een bezoek aan Nederland',
# 'van buitenlandse zaken brengt een bezoek aan Nederland vandaag', 'buitenlandse zaken', 'buitenlandse zaken brengt een bezoek aan',
# 'buitenlandse zaken brengt een bezoek aan Nederland', 'buitenlandse zaken brengt een bezoek aan Nederland vandaag', 'brengt een bezoek aan',
# 'brengt een bezoek aan Nederland', 'brengt een bezoek aan Nederland vandaag', 'Nederland', 'Nederland vandaag', 'vandaag']

phrase = 'a b c' #mapped to a1 b1 c1 d1 as followed
alignements = [[0,0],[1,1],[2,2],[0,3]]
print(extractPhrases(phrase,alignements))

#test with today(beginning) and vandaag(end)
#Problem :      a1   b1   c1   a2
#            a  .              .
#            b       .
#            c           .
#Desired output : b, c, bc, abc
