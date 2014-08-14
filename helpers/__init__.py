
_parallelF = ['wait_for_kill', 'getView', 'useDill', ]
_displayF = ['Table', 'describe', 'isNormal', 'figuresToLaTeX', 'rstyle', ]
_generalF = ['restoreOrCreateAndSave','loadRoot']

import parallel
import display
import general

for _x in _parallelF:
    locals()[_x] = getattr(parallel, _x)

for _x in _displayF:
    locals()[_x] = getattr(display, _x)

for _x in _generalF:
    locals()[_x] = getattr(general, _x)

#print locals()
__all__ = _parallelF + _displayF + _generalF
