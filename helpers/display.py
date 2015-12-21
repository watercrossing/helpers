from IPython.display import Math, HTML
import os.path, re
from itertools import * 
class Table(object):
    """
    Creates a flexible table object. Allows dynamically adding rows.
    Can export as html for display in the notebook, as well as latex for proper reports.
    """
    regexps = [(re.compile(r'(?<![\\])([#%&_\\{\\}])'),r'\\\1'), (re.compile(r'(?<![\\])([\^~])'),r'\\\1{}'), 
               (re.compile(r'(?<![\\])\\(?=\\)'),r'\\textbackslash{}')]
    
    TEST = 125
    @classmethod
    def fixStringForLaTeX(cls, string):
        for r, t in cls.regexps:
            string = r.sub(t, str(string))
        return string
    
    def __init__(self, columnDefinitions, latexColumnDefinitions = None):
        self.columns = columnDefinitions
        self.latexColumns = latexColumnDefinitions if latexColumnDefinitions else []
        self.rows = []
        
        self.caption = ""
        self.isFloat = True
        self.isLongTable = False
        self.isTableStar = False
        self.title = ""
        self.reference = ''
        self.header = None
        self.latexComment = ""
        self.headerRotate = False
        self.headerColours = []
        self.cellColours = []

    @staticmethod
    def _addColoursToLatexRow(row, colours):
        return row if not colours else [t if not c else "\\cellcolor[RGB]{%3d,%3d,%3d} %s" %(c[0],c[1],c[2],t) 
                                       for c, t in zip(colours, row)]

    def setHeader(self, row = [], cellColours = [], rotate=False):
        assert len(self.columns) == len(row)
        if cellColours:
            assert len(self.columns) == len(cellColours)
            assert all(len(x) == 4 for x in cellColours if x)
            # We can't handle alphas
            assert all(x[3] == 255 for x in cellColours if x)
        if rotate:
            if type(rotate) == type(list()):
                assert len(rotate) == len(self.columns)
            self.headerRotate = rotate
        self.headerColours = cellColours
        self.header = row
    
    def addRow(self, row = [], cellColours = []):
        """
        cellColours is a list of (r, g, b, 1) (one is the alpha), r,g,b integers [0,255]
        """
        assert len(self.columns) == len(row)
        if cellColours:
            assert len(self.columns) == len(cellColours)
            assert all(len(x) == 4 for x in cellColours if x)
            # We can't handle alphas
            assert all(x[3] == 255 for x in cellColours if x)
        self.cellColours.append(cellColours)
        self.rows.append(row)
    
    def fromNPArray(self, values, formatstr,  rowdesc=[], cellColours=None):
        """
        fills all the data from an np.ndarray. Sets call the cell background colour from another ndarray of 
        bytes=True plt.cm, i.e. plt.cm.summer(values,bytes=True).
        """
        assert values.shape[1] + int(bool(rowdesc)) == len(self.columns)
        if rowdesc:
            assert len(rowdesc) == values.shape[0]
        if cellColours is not None:
            assert values.shape + (4,) == cellColours.shape
            if rowdesc:
                self.cellColours = [[False] + row.tolist() for row in cellColours]
            else: 
                self.cellColours = cellColours.tolist()
        else:
           self.cellColours = [[] for _ in range(values.shape[0])]
        self.rows = [rowdesc[i:i+1] + [formatstr %x for x in row] for i, row in enumerate(values)]
        
    def setCaption(self, text = ""):
        self.caption = text

    def display(self):
        import IPython.display 
        IPython.display.display(self)

    def _repr_html_(self):
        s = u"""<style type="text/css">
    #{0} {{
        border-style:none !important;
        border:5px none black !imporant;
    }}
    #{0} tr {{
        border-style:none !important;
        border:5px none black !imporant;
    }}
    #{0} th {{
        padding:0.4em 0.6em;
        border: 1px double #000000 !important;
        border-style:none none double !important;
    }}
    #{0} th.rotate {{
        height: 140px;
        white-space: nowrap;
    }}
    #{0} th.rotate > div {{
        transform: 
          /* Magic Numbers */
          translate(25px, 51px)
          /* 45 is really 360 - 45 */
          rotate(315deg);
        width: 30px;
    }}
    #{0} td {{
        padding:0.2em 0.6em;
        border-style:none !important;
    }}
    #{0} td.c, #{0} th.c {{
        text-align:center;
    }}
    #{0} td.l, #{0} th.l {{
        text-align:left;
    }}
    #{0} td.r, #{0} th.r {{
        text-align:right;
    }}
</style>\n""".format('t%d' %id(self))
        s += u'<table id="t%d">\n' %id(self)
        if self.caption:
            s += u'<caption>%s</caption>\n' %self.caption
        if self.latexComment:
            s += self.latexComment + u"\n</br>\n"
        if self.header: 
            s += u'   <tr>' + u''.join([u'<th class="%s%s%s%s</th>' %(self.columns[i]," rotate\"><div>" if self.headerRotate and ((type(self.headerRotate) == type(list()) and self.headerRotate[i]) or (type(self.headerRotate) != type(list()) and i>0)) else "\">", x,"</div>" if self.headerRotate and ((type(self.headerRotate) == type(list()) and self.headerRotate[i]) or (type(self.headerRotate) != type(list()) and i>0)) else "" ) 
                                        for i, x in enumerate(self.header)]) + u'</tr>\n'
        for row,rowcol in zip(self.rows,self.cellColours):
            s += u'   <tr>' + u''.join([u'<td class="%s"%s>%s</td>' %(self.columns[i],u"" if not rowcol or not rowcol[i] else u" bgcolor=\"#%2X%2X%2X\"" %(rowcol[i][0],rowcol[i][1],rowcol[i][2]),x) 
                                        for i, x in enumerate(row)]) + u'</tr>\n'
        
            
        s += u'</table>'
        return s

    def compileLatexTable(self):
        """
        Returns touple (header, content), where header is a list and content is a list of lists.
        """
        if self.header:
            hc = [self.fixStringForLaTeX(x) for x in self.header]
            if self.headerRotate:
                if type(self.headerRotate) == type(list()):
                    rots = self.headerRotate
                else:
                    rots = [False] + [True]*(len(self.header) -1)
                rots = ["" if not x else "\\rot%s{" %("" if type(x) == type(True) else "[%s]" %s) for x in rots]
            hc = ["%s%s%s" %(r, c, "}" if r else "") for r,c in zip(rots,hc)]
        

            header = Table._addColoursToLatexRow(hc, self.headerColours)
        else:
            header = None
        rows = [Table._addColoursToLatexRow([self.fixStringForLaTeX(x) for x in row],cs) for row,cs in zip(self.rows, self.cellColours)]

        #now fix spacings
        rs = izip(*rows) if not header else izip(header,*rows)
        lens = [max(len(str(x)) for x in y) for y in rs]
        lens = [-x if self.columns[i] == 'l' else x for i,x in enumerate(lens)]
        if header:
            header = [self.fixElement(*x) for x in zip(header, [len(hx) for hx in hc], lens)]
        rows = [[self.fixElement(x[0],len(self.fixStringForLaTeX(x[1])),x[2]) for x in zip(row, rawRow, lens)] for row, rawRow in zip(rows, self.rows)]
        return header, rows

    def fixElement(self, t, rawLen, width):
        l = len(t)
        lr = rawLen
        return "%s%*s" %(t[0:l-lr], width/abs(width)*(abs(width)-(l-lr)), t[l-lr:])
        
    def _repr_latex_(self):
        if self.isFloat and not self.isLongTable:
            s = u'\\begin{table%s}[htb!]\n\\centering\n' %("*" if self.isTableStar else "")
        else:
            s = ''
            if self.isLongTable:
                s += u"\subsection{%s}\n\label{sec:%s}\n\n" %(self.title or self.reference, self.reference)
            if self.caption:
                s += u"\n\n".join([u'%s %s' %(u'%%' if not self.isLongTable else "",self.fixStringForLaTeX(x)) 
                                   for x in self.caption.splitlines()]) + u'\n'
            s += "\\begin{center}\n"
        if self.latexComment:
            s += u''.join([u'%%%s\n' %x for x in self.latexComment.splitlines()])
        s += u"\\begin{%s}{%s}\n" %(u'tabular' if not self.isLongTable else u'longtable',
                                    u''.join(self.latexColumns or self.columns))

        header, rows = self.compileLatexTable() 
        if self.header:
            #s += " Code& F. in A& F. in B& F. in C& F. in D& Label\\\\ \\hline\\hline\\\\[-1.em]\n"
            s += u'   %s \\\\ \\hline\\hline\\\\[-1.em]\n' %(u" & ".join(header))
        for row in rows:
            s += u'   %s \\\\[0.3em]\n' %(u" & ".join(row))
        s += "\\end{%s}\n" %(u'tabular' if not self.isLongTable else u'longtable')
        if self.isFloat and not self.isLongTable:
            if self.caption:
                s += u'\\caption{%s}\n' %self.fixStringForLaTeX(self.caption)
            if self.reference:
                s += u'\\label{tab:%s}\n' %self.reference
            s+= u"\\end{table%s}\n"  %("*" if self.isTableStar else "")
        else:
            s+= u"\\end{center}\n"
        return s
    
    @property
    def latex(self):
        return Math(self._repr_latex_())
    
    @property
    def html(self):
        return HTML(self._repr_html_())
    
    def writeLatexToFile(self, filename = '', path = ''):
        if not filename:
            if self.reference: 
                filename = self.reference
            else:
                filename = 'Untitled.tex'
        if not os.path.isabs(path):
            path = os.path.realpath(os.path.join(os.getcwd(),path))
        if filename[-4:] != '.tex': filename += '.tex'
        with open(os.path.join(path,filename), 'wb') as f:
            f.write(self._repr_latex_())
       
def describe(values):
    import scipy.stats
    describe = scipy.stats.describe(values)
    return "Size: %d, min: %g, max: %g, mean: %g, variance: %g, skewness: %g" %(
                describe[0],describe[1][0],describe[1][1],describe[2],describe[3],describe[4])
def isNormal(values):
    import scipy.stats
    t = scipy.stats.normaltest(values)
    if t[1] < 0.001: 
        s = "***"
    elif t[1] < 0.01:
        s = "**"
    elif t[1] < 0.05:
        s = "*"
    else:
        s = "-ns"
    return "Normaltest: s^2 + k^2 = %g, p = %.5g%s" %(t[0],t[1],s)

class figuresToLaTeX(object):
    columns = 1
    caption = ""
    figures = None
    regexps = [(re.compile(r'(?<![\\])%'),r'\\%')]
    
    @classmethod
    def fixStringForLaTeX(cls, string):
        for r, t in cls.regexps:
            string = r.sub(t, string)
        return string
    
    def __init__(self, columns = 1, caption = "", basename = "", path = ".", 
                 totalWidth = 1.0, totalWidthScale = '\\textwidth'):
        self.columns = columns
        self.caption = caption
        self.basename = basename
        self.totalWidth = totalWidth
        self.totalWidthScale = totalWidthScale
        self.path = path
        self.figures = []
    
    """
    Takes a pyplot plot, calls savefig on it and saves it in the /img/ directory
    """
    def addFigure(self, figure, subcaption = '', describeText = ''):
        
        fn = u'%s-%s' %(self.basename, len(self.figures))
        self.figures.append((fn, subcaption, describeText))
        figure.savefig(os.path.join(self.path, 'img', fn + '.pdf'),bbox_inches='tight')
        figure.savefig(os.path.join(self.path, 'img', fn + '-transparent.pdf'),bbox_inches='tight',transparent=True)
    
    @classmethod
    def makeIncludeGraphics(cls, figure, width=1.0, scale= u'\\textwidth'):
        s = u'\\includegraphics[width=%g%s]{%s}\n' %(width, scale,figure[0])
        s += u''.join([u'%%%s\n' %x for x in figure[2].splitlines()])

        return s
    
    @classmethod
    def makeSubFigure(cls, content, width= 1.0, scale= u'\\textwidth', caption = '', label = ''):
        s = u'\\begin{subfigure}[t]{%g%s}\n' %(width, scale)
        s += u'  \\centering\n'
        s += u''.join(['  %s\n' %x for x in content.splitlines()])
        if caption:
            s += u'  \\caption{%s}\n' %cls.fixStringForLaTeX(caption)
        s += u'  \\label{fig:%s}\n' %label
        s += u'\\end{subfigure}'
        return s
    
    @classmethod
    def makeFigure(cls, content, caption  = '', label = ''):
        s = u'\\begin{figure}[htb!]\n'
        s += u'  \\centering\n'
        s += u''.join(['  %s\n' %x for x in content.splitlines()])
        s += u'  \\caption{%s}\n' %cls.fixStringForLaTeX(caption)
        s += u'  \\label{fig:%s}\n' %label
        s += u'\\end{figure}'
        return s
    
    def getFigure(self):
        s = u''
        if len(self.figures) == 1:
            s += self.makeFigure(self.makeIncludeGraphics(self.figures[0],
                                                          width = self.totalWidth,
                                                          scale = self.totalWidthScale),
                                 caption = self.caption, label = self.basename)
        else:
            subwidth = self.totalWidth / self.columns
            for i, fig in enumerate(self.figures):
                s += self.makeSubFigure(self.makeIncludeGraphics(fig),
                                        width = subwidth, scale = self.totalWidthScale,
                                        caption = fig[1], label=fig[0])
                if i != len(self.figures) - 1 : 
                    s += u'\\\\ \n' if (i + 1) % self.columns == 0 else u'%\n'
            s = self.makeFigure(s, caption = self.caption, label = self.basename)
        return s
                    
    def writeLaTeX(self):
        with open(os.path.join(self.path, 'tex', self.basename + '.tex'), 'wb') as f:
            f.write(self.getFigure())

def rstyle(ax):
    """Styles an axes to appear like ggplot2
    Must be called after all plot and axis manipulation operations have been carried out
    """
    import matplotlib.pyplot as plt
    #set the style of the major and minor grid lines, filled blocks
    ax.grid(True, 'major', color='w', linestyle='-', linewidth=1.4)
    ax.grid(True, 'minor', color='0.95', linestyle='-', linewidth=0.7)
    ax.patch.set_facecolor('0.93')
    ax.set_axisbelow(True)
   
    #set minor tick spacing to 1/2 of the major ticks
    ax.xaxis.set_minor_locator(plt.MultipleLocator( (plt.xticks()[0][1]-plt.xticks()[0][0]) / 2.0 ))
    ax.yaxis.set_minor_locator(plt.MultipleLocator( (plt.yticks()[0][1]-plt.yticks()[0][0]) / 2.0 ))
   
    #remove axis border
    #for child in ax.get_children():
        #if isinstance(child, plt.matplotlib.spines.Spine):
            #child.set_alpha(0)
       
    #restyle the tick lines
    for line in ax.get_xticklines() + ax.get_yticklines():
        line.set_markersize(5)
        line.set_color("gray")
        line.set_markeredgewidth(1.4)
   
    #remove the minor tick lines    
    for line in ax.xaxis.get_ticklines(minor=True) + ax.yaxis.get_ticklines(minor=True):
        line.set_markersize(0)
   
    #only show bottom left ticks, pointing out of axis
    plt.rcParams['xtick.direction'] = 'out'
    plt.rcParams['ytick.direction'] = 'out'
    
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    plt.rc('font', **{'family':'serif', 'serif':['Computer Modern Roman'], 
                                        'monospace': ['Computer Modern Typewriter'],
                                        'sans-serif': ['Computer Modern Sans serif']})
   
    if ax.legend_ <> None:
        lg = ax.legend_
        lg.get_frame().set_linewidth(0)
        lg.get_frame().set_alpha(0.5)


