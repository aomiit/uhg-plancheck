'''
Created on 25 Jan 2012

@author: french_j
'''
def write(msg,tag,log):
    numlines = log.index('end - 1 line').split('.')[0]
    log['state'] = 'normal'
    if numlines==24:
        log.delete(1.0, 2.0)
    if log.index('end-1c')!='1.0':
        log.insert('end', '\n')
    log.insert('end', msg,tag)
    log['state'] = 'disabled'