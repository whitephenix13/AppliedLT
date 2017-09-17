DATA_DIR  = 'data/'

#Loaded files
f_en = open(DATA_DIR+'file.en', 'r')
f_de = open(DATA_DIR+'file.de', 'r')
f_align = open(DATA_DIR + 'file.aligned', 'r')

#phrase is the phrase as a string
#alignment is a list of pairs as follow : [[0,0],[0,1],[1,2]] ...
def extractPhrases(phrase,alignements):
    words = phrase.split()
    prevBox=[-1,-1,-1,-1] #Used to check if a word align outside of the phrase
    currentPhrase = "" # The current small phrase that is being built

    smallestPhrases=[] # A small phrase is defined by a phrase in which if you remove a word, it will no longer be a phrase
    for word_ind in range(len(words)) :
        if (currentPhrase == ""):
            currentPhrase = words[word_ind]
        else:
            currentPhrase += " " + words[word_ind]

        if(checkCorrectPhrase(prevBox,word_ind,alignements)):
            smallestPhrases.append(currentPhrase)
            currentPhrase=""
            prevBox = [-1, -1, -1, -1]

        else:
            prevBox = computePhraseBox(prevBox, alignements[word_ind])

    if(len(currentPhrase)>0):
        smallestPhrases.append(currentPhrase)
    print("Smallest phrases : " + str(smallestPhrases))
    return generateAllPhrases(smallestPhrases)
#Check if a phrase is correct by looking if no words are aligned to the outside
#newWordIndex: index of the new word in the phrase
#alignement: list of pairs as follow : [[0,0],[0,1],[1,2]] ...
def checkCorrectPhrase(prevBox,newWordIndex,alignements):
    newBox= computePhraseBox(prevBox,alignements[newWordIndex])
    #test if there is no alignment of a word in the box (either en or de) to a word outside it
    #Maily, test if there is no alignement [x,y] such that x in the box but not y , or the opposite
    correct=True
    for pair in alignements :
        x_in_box = (newBox[0]<=pair[0]) and (pair[0]<=newBox[2])
        y_in_box = (newBox[1]<=pair[1]) and (pair[1]<=newBox[3])
        if( (x_in_box and not y_in_box) or (not x_in_box and y_in_box)):
            correct=False
            break
    return correct
# Compute the box associated to the phrase. The computation is done by extending the box due to the addition of a word to the phrase.
#ie: box is [0,1,2,3] (alignments are within the points (0,1) and (2,3)) and we want to add a new word which has the following alignment:
#(2,4), the box will then be extended as [0,1,2,4]
# prevBox: index of the words in the phrase: This is my desk , "my desk" => [2,3],  [-1,-1,-1,-1] if none
# newAlignment: alignement corresponding to the new word in the format [x,y]
def computePhraseBox(prevBox, newAlignment):
    x=newAlignment[0]
    y=newAlignment[1]
    if(prevBox[0]==-1):
        return [x,y,x,y]
    else:
        if(prevBox[0]>x):
            prevBox[0]=x
        if (prevBox[1] > y):
            prevBox[1] = y
        if (prevBox[2] < x):
            prevBox[2] = x
        if (prevBox[3] < y):
            prevBox[3] = y
    return prevBox

#Given small phrases, generate all combination of those to make a bigger one
#ie: smallestPhrases = ["I","dream of","sleeping"] =>
#['I', 'I dream of', 'I dream of sleeping', 'dream of', 'dream of sleeping', 'sleeping']
def generateAllPhrases(smallestPhrases):
    allPhrases=[]
    for i in range(len(smallestPhrases)):
        for j in range(i,len(smallestPhrases)):
            newPhrase =smallestPhrases[i]
            for k in range(i+1,j+1):
                newPhrase+=(" "+ smallestPhrases[k])
            allPhrases.append(newPhrase)
    return allPhrases

phrase = 'De minister van buitenlandse zaken brengt een bezoek aan The Nederland'
alignements = [[0,0],[1,1],[2,2],[3,3],[4,3],[5,4],[6,4],[7,4],[8,4],[9,5],[9,6]]
print(extractPhrases(phrase,alignements))