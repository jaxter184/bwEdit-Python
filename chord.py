def bigOrd(text):
    output = 0
    for i in range(len(text)):
        #print(len(text)-i - 1)
        output += (256**(len(text)-i - 1))*ord(text[i])
    return output

#def getString(text, 
