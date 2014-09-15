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
    
    def setHeader(self, row = []):
        assert len(self.columns) == len(row)
        self.header = row
    
    def addRow(self, row = []):
        assert len(self.columns) == len(row)
        self.rows.append(row)
    
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
        if self.header: 
            s += u'   <tr>' + u''.join([u'<th class="%s">%s</th>' %(self.columns[i],x) 
                                        for i, x in enumerate(self.header)]) + u'</tr>\n'
        for row in self.rows:
            s += u'   <tr>' + u''.join([u'<td class="%s">%s</td>' %(self.columns[i],x) 
                                        for i, x in enumerate(row)]) + u'</tr>\n'
        
            
        s += u'</table>'
        return s
        
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
        s += u"\\begin{%s}{%s}\n" %(u'tabular' if not self.isLongTable else u'longtable',
                                    u''.join(self.latexColumns or self.columns))
        sp = self._getSpacingForRows()
        if self.header:
            #s += " Code& F. in A& F. in B& F. in C& F. in D& Label\\\\ \\hline\\hline\\\\[-1.em]\n"
            s += u'   ' + u" & ".join(['%*s' %(sp[i],self.fixStringForLaTeX(x))
                        for i, x in enumerate(self.header)]) + u" \\\\ \\hline\\hline\\\\[-1.em]\n"
        for row in self.rows:
            s += u'   ' + u" & ".join(['%*s' %(sp[i],self.fixStringForLaTeX(x)) for i, x in enumerate(row)]) + u" \\\\[0.3em]\n"
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
    
    def _getSpacingForRows(self):
        rs = izip(*self.rows) if not self.header else izip(self.header,*self.rows)
        lens = [max(len(str(x)) for x in y) for y in rs]
        lens = [-x if self.columns[i] == 'l' else x for i,x in enumerate(lens)]
        return lens
        
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
                                        'sans-serif': ['Computer Modern Sans serif'})
   
    if ax.legend_ <> None:
        lg = ax.legend_
        lg.get_frame().set_linewidth(0)
        lg.get_frame().set_alpha(0.5)


