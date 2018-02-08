from assembly2lib import *
from assembly2solver import solveConstraints

class CircularEdgeSelectionGate:
    def allow(self, doc, obj, sub):
        return CircularEdgeSelected( SelectionExObject(doc, obj, sub) )

class boltMultipleCircularEdgesCommand:
    def Activated(self):
        selection = FreeCADGui.Selection.getSelectionEx()
        if len(selection) < 2:
            FreeCADGui.Selection.clearSelection()
            self.taskDialog = RapidBoltingTaskDialog()
            FreeCADGui.Control.showDialog( self.taskDialog )
            FreeCADGui.Selection.removeSelectionGate()
            FreeCADGui.Selection.addSelectionGate( CircularEdgeSelectionGate() )
        else:
            valid = True
            for s in selection:
                for se_name in s.SubElementNames:
                    if not CircularEdgeSelected( SelectionExObject(FreeCAD.ActiveDocument, s.Object, se_name) ):
                        valid = False
                        break
            if valid:
                boltSelection()
            else:
                QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Usage Incorrect ", 'Selectionnez uniquement les bords circulaires')
    def GetResources(self): 
        msg = 'Fixer plusieurs bords circulaires'
        return {
            'Pixmap' : ':/assembly2/icons/boltMultipleCircularEdges.svg', 
            'MenuText': msg, 
            'ToolTip': msg
            } 

FreeCADGui.addCommand('boltMultipleCircularEdges', boltMultipleCircularEdgesCommand())

class RapidBoltingTaskDialog:
    def __init__(self):
        self.form = RapidBoltingForm('''Instructions:

1) selectionner le bord d accouplement sur le boulon
2) ajouter a la selection les bords
auquel le boulon doit etre accouple
3) presser Ok ''' )
        self.form.setWindowTitle( 'Bolt multiple circular edges' )    
        self.form.setWindowIcon( QtGui.QIcon( ':/assembly2/icons/boltMultipleCircularEdges.svg' ) )
    def reject(self):
        FreeCADGui.Selection.removeSelectionGate()
        FreeCADGui.Control.closeDialog()
    def accept(self):
        FreeCADGui.Selection.removeSelectionGate()
        FreeCADGui.Control.closeDialog()
        boltSelection()
class RapidBoltingForm(QtGui.QWidget):    
    def __init__(self, textLines ):
        super(RapidBoltingForm, self).__init__()
        self.textLines = textLines 
        self.initUI()
    def initUI(self):
        vbox = QtGui.QVBoxLayout()
        for line in self.textLines.split('\n'):
            vbox.addWidget( QtGui.QLabel(line) )
        self.setLayout(vbox)


from circularEdgeConstraint import parseSelection
from importPart import duplicateImportedPart

def boltSelection():
    doc = FreeCAD.ActiveDocument
    doc.openTransaction('Fixer plusieurs bords circulaires')
    selection = FreeCADGui.Selection.getSelectionEx()
    bolt = selection[0].Object
    bolt_se_name = selection[0].SubElementNames[0]
    S = [] #edgesToConstrainTo 
    for s in selection[1:]:
        for se_name in s.SubElementNames:
            S.append( SelectionExObject(doc, s.Object, se_name) )
    for s2 in S:
        newBolt = duplicateImportedPart(bolt)
        s1 = SelectionExObject(doc, newBolt, bolt_se_name)
        debugPrint(3,'s1 %s' % [s1, s2])
        parseSelection(
            [s1, s2 ], 
            callSolveConstraints= False, lockRotation = True 
            )
    solveConstraints( doc )
    FreeCAD.ActiveDocument.commitTransaction()
    repair_tree_view()
