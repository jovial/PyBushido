import injections
from bushido import partial_compare_list

def compare(data,template):
    data = list(data)
    for index, value in enumerate(template):
        if value == '*':
            data[index] = value
    return partial_compare_list(template,data)
    
    
def injectReceive(data):
    reload(injections)
    for matcher,replacements in injections.receive_injections:
        injectOnMatch(data,matcher,replacements)
        
def injectTransmit(data):
    reload(injections)
    for matcher,replacements in injections.transmit_injections:
        injectOnMatch(data,matcher,replacements)

def injectOnMatch(data, matcher,replacements):
    if compare(data,matcher):
        for index,value in enumerate(replacements):
            if value != '*':
                data[index] = value
    return data    
    
if __name__ == '__main__':
    test = [0xdc, 0x02, 0x00, 0x99, 0x00, 0x00, 0x00, 0x00]
    print test
    injectReceive(test)
    print test
    test = [0xdc, 0x02, 0x00, 0x99, 0x00, 0x00, 0x00, 0x00]
    print test
    injectTransmit(test)
    print test