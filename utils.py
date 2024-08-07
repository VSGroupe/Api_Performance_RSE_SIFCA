import re
def AplusB(A, B):
    if A != None and B != None:
        return A + B
    elif A == None and B != None:
        return B
    elif A != None and B == None:
        return A
    else:
        return None

def CompareAandB(A, B):
    if A != None and B != None:
        return A == B
    elif A == None and B == None:
        return None
    else:
        return False
    
def PerformGlobal(liste):
    filtreList = [x for x in liste if x is not None ]
    if not filtreList:
        return 0  
    average = sum(filtreList) / len(filtreList)
    return average

def extraire_chiffres(chaine):
    chiffres = re.findall(r'\d+', chaine)
    chiffres_concatenes = ''.join(chiffres)
    return chiffres_concatenes

def indexes_by(dicts_list, value):
    indexes_dict = {}
    for index, d in enumerate(dicts_list):
        tempVal = d[f'{value}']
        if tempVal is not None:
            if tempVal in indexes_dict:
                indexes_dict[tempVal].append(index)
            else:
                indexes_dict[tempVal] = [index]
    return list(indexes_dict.values())

def checkProcessValue(index, listDic):
    value = listDic[index].get('processus')
    
    if value is not None:
        return True
    return False

def AfoisB(A, B):
    if A != None and B != None:
        return A * B
    else:
        return None

def sommeList(list):
    a = None
    for i in range(len(list)):
        a = AplusB(a, list[i])
    return a

def AmoinsB(A, B):
    if A != None and B != None:
        return A - B
    else:
        return None

def AsurB(A, B):
    try:
        C = A / B
        return C
    except:
        return None

def AsurV(A, V):
    try:
        C = A / V
        return C
    except:
        return None

def formuleSomme(dataRow) :
    l = []
    for data in dataRow :
        if data != None :
            l.append(data)
    if l != [] :
        return sum(l)
    return None

def formuleDernierMois(dataRow) :
    l = []
    for data in dataRow :
        if data != None :
            l.append(data)
    if l != [] :
        return l[-1]
    return None

def formuleMoyenne(dataRow) :
    l = []
    for data in dataRow :
        if data != None :
            l.append(data)
    if l != [] :
        total = sum(l)
        average = total / len(l)
        return average
    return None

def testIndicatorsFormulas(index, dataValeurList, dataValeurListPastYear):
    try:
        if index == 55:
            # if : L54 + L53 = L49
            computeList = []
            list = []
            A = dataValeurList[53]
            B = dataValeurList[52]
            C = dataValeurList[48]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                computeList.append(valeur)
            for i in range(len(computeList)):
                valeur = CompareAandB(computeList[i], C[i])
                if valeur:
                    list.append(1)
                elif valeur == False:
                    list.append(0)
                else:
                    list.append(valeur)
            return list
        elif index == 60:
            # if : L56 + L57 + L58 + L59 = L49
            computeList = []
            resultlist = []
            A = dataValeurList[55]
            B = dataValeurList[56]
            C = dataValeurList[57]
            D = dataValeurList[58]
            E = dataValeurList[48]
            setList = [C, D]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                computeList.append(valeur)
            for list in setList:
                for i in range(len(computeList)):
                    valeur = AplusB(computeList[i], list[i])
                    computeList[i] = valeur
            #print(len(computeList))
            for i in range(len(computeList)):
                valeur = CompareAandB(computeList[i], E[i])
                if valeur == True:
                    resultlist.append(1)
                elif valeur == False:
                    resultlist.append(0)
                else:
                    resultlist.append(valeur)
            #print(len(resultlist))
            return resultlist
        elif index == 69:
            # if : L65 + L66 + L67 + L68 = L54
            computeList = []
            resultList = []
            A = dataValeurList[64]
            B = dataValeurList[65]
            C = dataValeurList[66]
            D = dataValeurList[67]
            E = dataValeurList[53]
            setList = [C, D]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                computeList.append(valeur)
            for list in setList:
                for i in range(len(computeList)):
                    valeur = AplusB(computeList[i], list[i])
                    computeList[i] = valeur
            for i in range(len(computeList)):
                valeur = CompareAandB(computeList[i], E[i])
                if valeur:
                    resultList.append(1)
                elif valeur == False:
                    resultList.append(0)
                else:
                    resultList.append(valeur)
            return resultList
        elif index == 73:
            # if : L70 + L71 + L72 = L49
            computeList = []
            resultList = []
            A = dataValeurList[69]
            B = dataValeurList[70]
            C = dataValeurList[71]
            D = dataValeurList[48]
            setList = [C]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                computeList.append(valeur)
            for list in setList:
                for i in range(len(computeList)):
                    valeur = AplusB(computeList[i], list[i])
                    computeList[i] = valeur
            for i in range(len(computeList)):
                valeur = CompareAandB(computeList[i], D[i])
                if valeur:
                    resultList.append(1)
                elif valeur == False:
                    resultList.append(0)
                else:
                    resultList.append(valeur)
            return resultList
        elif index == 77:
            # if : L74 + L75 + L76 = L53
            computeList = []
            resultList = []
            A = dataValeurList[73]
            B = dataValeurList[74]
            C = dataValeurList[75]
            D = dataValeurList[52]
            setList = [C]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                computeList.append(valeur)
            for list in setList:
                for i in range(len(computeList)):
                    valeur = AplusB(computeList[i], list[i])
                    computeList[i] = valeur
            for i in range(len(computeList)):
                valeur = CompareAandB(computeList[i], D[i])
                if valeur:
                    resultList.append(1)
                elif valeur == False:
                    resultList.append(0)
                else:
                    resultList.append(valeur)
            return resultList
        elif index == 81:
            # if : L78 + L79 + L80 = L54
            computeList = []
            resultList = []
            A = dataValeurList[77]
            B = dataValeurList[78]
            C = dataValeurList[79]
            D = dataValeurList[53]
            setList = [C]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                computeList.append(valeur)
            for list in setList:
                for i in range(len(computeList)):
                    valeur = AplusB(computeList[i], list[i])
                    computeList[i] = valeur
            for i in range(len(computeList)):
                valeur = CompareAandB(computeList[i], D[i])
                if valeur:
                    resultList.append(1)
                elif valeur == False:
                    resultList.append(0)
                else:
                    resultList.append(valeur)
            return resultList
        elif index == 86:
            # if : L90 + L94 = L95
            computeList = []
            resultList = []
            A = dataValeurList[89]
            B = dataValeurList[93]
            C = dataValeurList[94]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                computeList.append(valeur)
            for i in range(len(computeList)):
                valeur = CompareAandB(computeList[i], C[i])
                if valeur:
                    resultList.append(1)
                elif valeur == False:
                    resultList.append(0)
                else:
                    resultList.append(valeur)
            return resultList
        elif index == 111:
            # if : L109 + L110 = L108
            computeList = []
            resultList = []
            A = dataValeurList[108]
            B = dataValeurList[109]
            C = dataValeurList[107]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                computeList.append(valeur)
            for i in range(len(computeList)):
                valeur = CompareAandB(computeList[i], C[i])
                if valeur:
                    resultList.append(1)
                elif valeur == False:
                    resultList.append(0)
                else:
                    resultList.append(valeur)
            return resultList
        elif index == 114:
            # Test de coherence, si : L49 (mois passe) + L96 - L113 = L49 alors vrai sinon faux
            # l'indexe 0 correspond au realisé
            computeList = []
            resultList = []
            A = dataValeurList[48]
            B = dataValeurList[95]
            C = dataValeurList[112]
            datasPastYear = dataValeurListPastYear[48]
            setList = [C]

            for i in range(len(B)):
                if i == 0:
                    valeur = AplusB(datasPastYear[i], B[i])
                    computeList.append(valeur)
                elif i == 1:
                    valeur = AplusB(datasPastYear[0], B[i])
                    computeList.append(valeur)
                else:
                    valeur = AplusB(B[i], A[i - 1])
                    computeList.append(valeur)
            for list in setList:
                for i in range(len(computeList)):
                    valeur = AmoinsB(computeList[i], list[i])
                    computeList[i] = valeur
            for i in range(len(computeList)):
                valeur = CompareAandB(computeList[i], A[i])
                if valeur:
                    resultList.append(1)
                elif valeur == False:
                    resultList.append(0)
                else:
                    resultList.append(valeur)
            return resultList
        
        return None
    except:
        return None

def formuleCalcules(index, dataValeurList):
    try:
        if index == 3:
            # L1 + L2
            list = []
            A = dataValeurList[0]
            B = dataValeurList[1]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 5:
            # L4 / L2
            list = []
            A = dataValeurList[3]
            B = dataValeurList[1]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 7:
            # L6 / L49
            list = []
            A = dataValeurList[5]
            B = dataValeurList[48]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 10:
            # L8 + L 9
            list = []
            A = dataValeurList[7]
            B = dataValeurList[8]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list     
        elif index == 12:
            # L11 / L3
            list = []
            A = dataValeurList[10]
            B = dataValeurList[2]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 19:
            # L18 / L17
            list = []
            A = dataValeurList[17]
            B = dataValeurList[16]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 23:
            # GOU3-010 = L45 / L3
            list = []
            A = dataValeurList[44]
            B = dataValeurList[2]
            for i in range (len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 24:
            # L26 / L13
            list = []
            A = dataValeurList[25]
            B = dataValeurList[12]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 27:
            # L32 / L16
            list = []
            A = dataValeurList[31] #25
            B = dataValeurList[15] #12
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 30:
            # L28 + L29
            list = []
            A = dataValeurList[27]
            B = dataValeurList[28]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 31:
            # L30 / L6
            list = []
            A = dataValeurList[29]
            B = dataValeurList[5]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 33:
            # L32 / L30
            list = []
            A = dataValeurList[31]
            B = dataValeurList[29]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 36:
            # L35 / L11
            list = []
            A = dataValeurList[34]
            B = dataValeurList[10]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 38:
            # L37 / L10
            list = []
            A = dataValeurList[36]
            B = dataValeurList[9]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 40:
            # L39 / L13
            list = []
            A = dataValeurList[38]
            B = dataValeurList[12]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 42:
            # L41 / L13
            list = []
            A = dataValeurList[40]
            B = dataValeurList[12]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 44:
            # L43 / L11
            list = []
            A = dataValeurList[42]
            B = dataValeurList[10]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 49:
            # L47 + L48
            list = []
            A = dataValeurList[46]
            B = dataValeurList[47]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 50:
            # L47 / L49
            list = []
            A = dataValeurList[46]
            B = dataValeurList[48]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 52:
            # L49 + L51
            list = []
            A = dataValeurList[48]
            B = dataValeurList[50]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 95:
            # L90 + L94
            list = []
            A = dataValeurList[89]
            B = dataValeurList[93]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 96:
            # L95 + L85
            list = []
            A = dataValeurList[94]
            B = dataValeurList[84]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 113:
            # L108 + L112
            list = []
            A = dataValeurList[107]
            B = dataValeurList[111]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 115:
            # L109 / L54
            list = []
            A = dataValeurList[108]
            B = dataValeurList[53]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 116:
            # L110 / L53
            list = []
            A = dataValeurList[109]
            B = dataValeurList[52]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 122:
            # L121 / L49
            list = []
            A = dataValeurList[120]
            B = dataValeurList[48]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 125:
            # L123 / L53
            list = []
            A = dataValeurList[122]
            B = dataValeurList[52]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 126:
            # L121 / L54
            list = []
            A = dataValeurList[120]
            B = dataValeurList[53]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 129:
            # L128 / L127
            list = []
            A = dataValeurList[127]
            B = dataValeurList[126]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 133:
            # L132 / L49
            list = []
            A = dataValeurList[131]
            B = dataValeurList[48]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 135:
            # L134 / L49
            list = []
            A = dataValeurList[133]
            B = dataValeurList[48]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 141:
            # L140 / L48
            list = []
            A = dataValeurList[139]
            B = dataValeurList[47]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 144:
            # L42 / L143
            list = []
            A = dataValeurList[141]
            B = dataValeurList[142]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 147:
            # L145 + L146
            list = []
            A = dataValeurList[144]
            B = dataValeurList[145]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 184:
            # L82 / L49
            list = []
            A = dataValeurList[181]
            B = dataValeurList[48]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 180:
            # L185 / L49
            list = []
            A = dataValeurList[184]
            B = dataValeurList[48]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 188:
            # L187/ L49
            list = []
            A = dataValeurList[186]
            B = dataValeurList[48]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 192:
            # L191 / L190
            list = []
            A = dataValeurList[190]
            B = dataValeurList[189]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 197:
            # L195 + L196
            list = []
            A = dataValeurList[194]
            B = dataValeurList[195]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 208:
            # L207 / L13
            list = []
            A = dataValeurList[206]
            B = dataValeurList[12]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 212:
            # L209 / L13
            list = []
            A = dataValeurList[208]
            B = dataValeurList[12]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 215:
            # L214 / L49
            list = []
            A = dataValeurList[213]
            B = dataValeurList[48]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 240:
            # L239 + L236
            list = []
            A = dataValeurList[238]
            B = dataValeurList[235]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 241:
            # L240 / L11
            list = []
            A = dataValeurList[239]
            B = dataValeurList[10]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 244:
            # L243 / L220
            list = []
            A = dataValeurList[242]
            B = dataValeurList[219]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 258:
            # L256 / L257
            list = []
            A = dataValeurList[255]
            B = dataValeurList[256]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 260:
            # L259 / L11
            list = []
            A = dataValeurList[258]
            B = dataValeurList[10]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 262:
            # L276 / L13
            list = []
            A = dataValeurList[275]
            B = dataValeurList[12]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 264:
            # L263 / L11
            list = []
            A = dataValeurList[262]
            B = dataValeurList[10]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 271:
            # L269 / L270
            list = []
            A = dataValeurList[268]
            B = dataValeurList[269]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 274:
            # L272 + L273
            list = []
            A = dataValeurList[271]
            B = dataValeurList[272]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 277:
            # L275 + L276
            list = []
            A = dataValeurList[274]
            B = dataValeurList[275]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 280:
            # L278 + L279
            list = []
            A = dataValeurList[277]
            B = dataValeurList[278]
            for i in range(len(A)):
                valeur = AplusB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 283:
            # GOU3-013 = L282 / L46
            list = []
            A = dataValeurList[281]
            B = dataValeurList[45]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 285:
            # INC7-013 = L284 / L218
            list = []
            A = dataValeurList[283]
            B = dataValeurList[217]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 287:
            # INC7-016 = L219 / L286
            list = []
            A = dataValeurList[218]
            B = dataValeurList[285]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 216:
            # INC7-019 = L281 / L288
            list = []
            A = dataValeurList[280]
            B = dataValeurList[287]
            for i in range(len(A)):
                valeur = AsurB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 65:
            # L56 - L61
            list = []
            A = dataValeurList[55]
            B = dataValeurList[60]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 66:
            # L57 - L62
            list = []
            A = dataValeurList[56]
            B = dataValeurList[61]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 67:
            # L58 - L63
            list = []
            A = dataValeurList[57]
            B = dataValeurList[62]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 68:
            # L59 - L64
            list = []
            A = dataValeurList[58]
            B = dataValeurList[63]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 78:
            # L70 - L74
            list = []
            A = dataValeurList[69]
            B = dataValeurList[73]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 79:
            # L71 - L75
            list = []
            A = dataValeurList[70]
            B = dataValeurList[74]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 80:
            # L72 - L76
            list = []
            A = dataValeurList[71]
            B = dataValeurList[75]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        
        elif index == 91:
            # L82 - L87
            list = []
            A = dataValeurList[81]
            B = dataValeurList[86]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 92:
            # L83 - L88
            list = []
            A = dataValeurList[82]
            B = dataValeurList[87]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 93:
            # L84 - L89
            list = []
            A = dataValeurList[83]
            B = dataValeurList[88]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 124:
            # L121 - L123
            list = []
            A = dataValeurList[120]
            B = dataValeurList[122]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 132:
            # L130 - L131
            list = []
            A = dataValeurList[129]
            B = dataValeurList[130]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 259:
            # L249 - L253
            list = []
            A = dataValeurList[248]
            B = dataValeurList[252]
            for i in range(len(A)):
                valeur = AmoinsB(A[i], B[i])
                list.append(valeur)
            return list
        elif index == 90:
            # L87 + L88 + L89
            list = []
            A = dataValeurList[86]
            B = dataValeurList[87]
            C = dataValeurList[88]
            for i in range(len(A)):
                valeurTemp = AplusB(A[i], B[i])
                valeur = AplusB(valeurTemp, C[i])
                list.append(valeur)
            return list
        elif index == 94:
            # L91 + L92 + L93
            list = []
            A = dataValeurList[90]
            B = dataValeurList[91]
            C = dataValeurList[92]
            for i in range(len(A)):
                valeurTemp = AplusB(A[i], B[i])
                valeur = AplusB(valeurTemp, C[i])
                list.append(valeur)
            return list
        elif index == 101:
            # L97 + L98 + L99 + L100
            list = []
            A = dataValeurList[96]
            B = dataValeurList[97]
            C = dataValeurList[98]
            D = dataValeurList[99]
            for i in range(len(A)):
                valeurTemp = AplusB(A[i], B[i])
                valeurTemp = AplusB(valeurTemp, C[i])
                valeur = AplusB(valeurTemp, D[i])
                list.append(valeur)
            return list
        elif index == 108:
            # L101 + L102 + L103 + L104 + L105 + L106 + L107
            list = []
            A = dataValeurList[100]
            B = dataValeurList[101]
            C = dataValeurList[102]
            D = dataValeurList[103]
            E = dataValeurList[104]
            F = dataValeurList[105]
            G = dataValeurList[106]
            setList = [A, B, C, D, E, F, G]

            for i in range(len(A)):
                valeur = None
                for sousList in setList:
                    valeur = AplusB(valeur, sousList[i])
                list.append(valeur)
            return list
        elif index == 121:
            # L117 + L118 + L119 + L120
            list = []
            A = dataValeurList[116]
            B = dataValeurList[117]
            C = dataValeurList[118]
            D = dataValeurList[119]
            setList = [A, B, C, D]

            for i in range(len(A)):
                valeur = None
                for sousList in setList:
                    valeur = AplusB(valeur, sousList[i])
                list.append(valeur)
            return list
        elif index == 227:
            # (L222 * 3.44 + L223 * 2.6 + L224 * 3 + L225 * 2.96 + L226 * 3.64 ) / 1000;
            list = [None, None, None, None, None, None, None, None, None, None, None, None, None]
            A = dataValeurList[221]
            B = dataValeurList[222]
            C = dataValeurList[223]
            D = dataValeurList[224]
            E = dataValeurList[225]
            coefList = [3.44, 2.6, 3, 2.96, 3.64]
            setList = [A, B, C, D, E]

            for i in range(1, len(A)):
                total = None
                for j in range(len(setList)):
                    product = AfoisB(setList[j][i], coefList[j])
                    total = AplusB(total, product)
                valeur = AsurB(total, 1000)
                list[i] = valeur

            list[0] = sommeList(list)

            return list
        elif index == 249:
            # L246 + L247 + L248
            list = []
            A = dataValeurList[245]
            B = dataValeurList[246]
            C = dataValeurList[247]
            for i in range(len(A)):
                valeurTemp = AplusB(A[i], B[i])
                valeur = AplusB(valeurTemp, C[i])
                list.append(valeur)
            return list
        elif index == 253:
            # L250 + L251 + L252
            list = []
            A = dataValeurList[249]
            B = dataValeurList[250]
            C = dataValeurList[251]
            for i in range(len(A)):
                valeurTemp = AplusB(A[i], B[i])
                valeur = AplusB(valeurTemp, C[i])
                list.append(valeur)
            return list
        elif index == 269:
            # L265 + L266 + L267
            list = []
            A = dataValeurList[264]
            B = dataValeurList[265]
            C = dataValeurList[266]
            for i in range(len(A)):
                valeurTemp = AplusB(A[i], B[i])
                valeur = AplusB(valeurTemp, C[i])
                list.append(valeur)
            return list
        elif index == 138:
            # L137 /(L58+L59)
            list = []
            A = dataValeurList[57]
            B = dataValeurList[58]
            C = dataValeurList[137]
            for i in range(len(A)):
                D = AplusB(A[i], B[i])
                valeur = AsurB(C[i], D[i])
                list.append(valeur)
            return list
        elif index == 139:
            # (L63+L64)/(L58+L59)
            list = []
            A = dataValeurList[62]
            B = dataValeurList[63]
            C = dataValeurList[57]
            D = dataValeurList[58]
            for i in range(len(A)):
                E = AplusB(A[i], B[i])
                F = AplusB(C[i], D[i])
                valeur = AsurB(E[i], F[i])
                list.append(valeur)
            return list
        elif index == 190:
            # L189 / 8
            list = []
            A = dataValeurList[188]
            V = 8
            for i in range(len(A)):
                valeur = AsurV(A[i], V)
                list.append(valeur)
            return list
        elif index == 198:
            # L198 x 1000000 / L189
            list = []
            A = dataValeurList[197]
            B = 1000000
            C = dataValeurList[188]
            for i in range(len(A)):
                valeur = AsurV(A[i], B)
                list.append(valeur)
            D = list
            list2 = []
            for i in range(len(C)):
                valeur = AsurV(D[i], C)
                list2.append(valeur)
            return list2
        elif index == 199:
            # L194 x 1000 / L189
            list = []
            A = dataValeurList[193]
            B = 1000
            C = dataValeurList[188]
            for i in range(len(A)):
                valeur = AsurV(A[i], B)
                list.append(valeur)
            D = list
            list2 = []
            for i in range(len(C)):
                valeur = AsurB(D[i], C[i])
                list2.append(valeur)
            return list2
        elif index == 231:
            # L229 x 2,7 + L230 x 3,16
            list = []
            A = dataValeurList[228]
            B = 2.7
            C = dataValeurList[229]
            D = 3.16

            for i in range(len(A)):
                valeur = AfoisB(A[i], B)
                list.append(valeur)
            E = list
            list2 = []
            for i in range(len(C)):
                valeur = AfoisB(C[i], D)
                list2.append(valeur)
            F = list2
            list3 = []
            for i in range(len(E)):
                valeur = AfoisB(E[i], F[i])
                list3.append(valeur)
            return  list3

        elif index == 234:
            # L232 x 2,7 + L233 x 3,04
            list = []
            A = dataValeurList[231]
            B = 2.7
            C = dataValeurList[232]
            D = 3.04
            for i in range(len(A)):
                E = AfoisB(A[i], B)
                F = AfoisB(C[i], D)
                valeur = AplusB(E, F)
                list.append(valeur)
            return list
        elif index == 239:
            # L238 x 0,445 / 1000
            list = []
            A = dataValeurList[237]
            B = 0.445
            C = 1000
            for i in range(len(A)):
                D = AfoisB(A[i], B)
                valeur = AsurB(D, C)
                list.append(valeur)
            return list

        return None
    except:
        return None


