# helpers
My set of IPython helper functions

Currently there are 


## Table class

A class for creating tables. These tables render as HTML in IPython, and can saved as LaTeX tabular floats or longtables. The table supports background colours (very useful for heatmaps), horizontal and vertical lines as well as turned headers. 

*Add some images here*


## figuresToLaTeX class

Takes matplotlib figures, saves them into pdf's and creates latex files that contain the float, figure, inputgraphics, caption and label. Can also handle subfigures.  

## Other Convenience Functions


### rstyle(ax)

There is also an rstyle function that styles axes so that they look like ggplot2. I suppose I could use `matplotlib.style`, but haven't gotten round to trying it out yet.

###  restoreOrCreateAndSave(path, createfun, *args)

Compute creatfun(args) only once. Saves the output pickled to path, and unpickles the output if the file exists. There might exist a IPython magic to do the same thing.

### loadRoot(filename)

Pretty much a `lxml.etree.parse(open(filename, 'rb')).getroot()` convenience function.

### wait_for_kill(asyncres, view, updateInterval = 1.)

shows the progress of async results and calls `view.shutdown()` once done.

### def getView():

gets a local or cluster client and returns  `cluster.load_balanced_view()`

### def useDill():

imports dill and uses it for `IPython.kernel.zmq.serialize`.


