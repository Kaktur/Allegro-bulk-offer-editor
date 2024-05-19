import json
# this script will add to the end of first section in offer description the next line from data.json
def main(offer_data,data):

    nr = 0
    #add nr to data dict if not already in
    if not data:
        data.append(nr)
    #get data
    else:
        nr = data[0]
    #get data from data.json
    with open('data\\patterns\\example\\data.json', mode = 'r') as file:
        lines = json.load(file)
    line = lines[nr]

    #extract wanted data from offer_data
    text = offer_data['description']['sections'][0]['items'][0]['content']

    #apply transformation
    t = text.split("</")
    text = f"{t[0]} {line} </{t[1]}"

    #add edited data to offer data
    offer_data['description']['sections'][0]['items'][0]['content'] = text

    #if nr bigger or equal to nr reset to 0
    if nr >= len(lines)-1:
        nr = 0
    else:
        nr += 1
    
    data[0] = nr
    return offer_data,data