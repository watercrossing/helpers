from IPython.core.display import clear_output
def wait_for_kill(asyncres, view, updateInterval = 1.):
    N = len(asyncres)
    print "%4i/%i tasks finished after %4i s" % (asyncres.progress, N, asyncres.elapsed), 
    while not asyncres.ready():
        asyncres.wait(updateInterval)
        clear_output()
        print "%4i/%i tasks finished after %4i s" % (asyncres.progress, N, asyncres.elapsed),
        sys.stdout.flush()
    print ""
    view.shutdown()
    print "done"
