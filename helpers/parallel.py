
def wait_for_kill(asyncres, view, updateInterval = 1.):
    from IPython.core.display import clear_output
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

def getView():
    from IPython.parallel import TimeoutError, Client
    try:
        cluster = Client(profile="sge")
        print "running on SGE"
    except (TimeoutError, IOError) as e:
        try:
            cluster = Client(profile="localcluster")
            print "running on the localcluster with %d threads." %len(cluster)
        except (TimeoutError, IOError) as f:
            print "Need to have at least one cluster running."
            print e
            raise f
    return cluster.load_balanced_view()


def useDill():
    # load dill
    import dill

    # disable special function handling
    from types import FunctionType
    from IPython.utils.pickleutil import can_map

    can_map.pop(FunctionType, None)

    # fallback to pickle instead of cPickle, so that dill can take over
    import pickle
    from IPython.kernel.zmq import serialize
    serialize.pickle = pickle


