def restoreOrCreateAndSave(path, createfun, *args):
    import cPickle
    import os.path
    import time
    try:
        quiet
    except NameError:
        toprint = True
    else:
        toprint = False
    t = None
    if os.path.exists(path):
        with open(path,'rb') as f:
            t = cPickle.load(f)
        if toprint: print "Variable was successfully restored from %s." %path
    else:
        start = time.time()
        t = createfun(*args)
        total = time.time()-start
        if toprint: print "Building %s took %.3f seconds" %(path,total)
        with open(path,'wb') as f:
            cPickle.dump(t,f,-1)
    return t

def loadRoot(filename):
    from lxml import etree
    with open(filename,'rb') as f:
        tree = etree.parse(f)
    return tree.getroot()
