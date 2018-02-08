from assembly2lib import *
from lib3D import *
from pivy import coin
from PySide import QtGui

__dir2__ = os.path.dirname(__file__)
GuiPath = os.path.expanduser ("~") #GuiPath = os.path.join( __dir2__, 'Gui' )

class CircularEdgeSelectionGate:
     def allow(self, doc, obj, sub):
          return ValidSelectionFunct(SelectionExObject(doc, obj, sub),doc, obj, sub)

def ValidSelectionFunct(selectionExObj, doc, obj, sub):
     return CircularEdgeSelected( SelectionExObject(doc, obj, sub) )\
         or AxisOfPlaneSelected(selectionExObj)
         
def parseSelection(selection, objectToUpdate=None, callSolveConstraints=True, lockRotation = False):
    validSelection = False
    if len(selection) == 2:
        s1, s2 = selection
        if s1.ObjectName != s2.ObjectName:
            validSelection = True
            cParms = [ [s1.ObjectName, s1.SubElementNames[0], s1.Object.Label ],
                       [s2.ObjectName, s2.SubElementNames[0], s2.Object.Label ] ]
            debugPrint(4,'cParms = %s' % (cParms))
    if not validSelection:
          msg = '''Pour ajouter une contrainte de contour circulaire, selectionnez deux aretes circulaires, chacune d une partie differente. Selection faite:
%s'''  % printSelection(selection)
          QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Incorrect Usage", msg)
          return 

    if objectToUpdate == None:
        cName = findUnusedObjectName('circularEdgeConstraint')
        debugPrint(2, "creating %s" % cName )
        c = FreeCAD.ActiveDocument.addObject("App::FeaturePython", cName)
                
        c.addProperty("App::PropertyString","Type","ConstraintInfo").Type = 'circularEdge'
        c.addProperty("App::PropertyString","Object1","ConstraintInfo").Object1 = cParms[0][0]
        c.addProperty("App::PropertyString","SubElement1","ConstraintInfo").SubElement1 = cParms[0][1]
        c.addProperty("App::PropertyString","Object2","ConstraintInfo").Object2 = cParms[1][0]
        c.addProperty("App::PropertyString","SubElement2","ConstraintInfo").SubElement2 = cParms[1][1]
    
        c.addProperty("App::PropertyEnumeration","directionConstraint", "ConstraintInfo")
        c.directionConstraint = ["none","aligne","oppose"]
        c.addProperty("App::PropertyDistance","offset","ConstraintInfo")
        c.addProperty("App::PropertyBool","lockRotation","ConstraintInfo").lockRotation = lockRotation
    
        c.setEditorMode('Type',1)
        for prop in ["Object1","Object2","SubElement1","SubElement2"]:
            c.setEditorMode(prop, 1) 
        
        c.Proxy = ConstraintObjectProxy()
        c.ViewObject.Proxy = ConstraintViewProviderProxy( c, ':/assembly2/icons/circularEdgeConstraint.svg', True, cParms[1][2], cParms[0][2])
    else:
        debugPrint(2, "redefining %s" % objectToUpdate.Name )
        c = objectToUpdate
        c.Object1 = cParms[0][0]
        c.SubElement1 = cParms[0][1]
        c.Object2 = cParms[1][0]
        c.SubElement2 = cParms[1][1]
        updateObjectProperties(c)
    constraintFile = os.path.join( GuiPath , 'constraintFile.txt')
    with open(constraintFile, 'w') as outfile:
         outfile.write(make_string(s1.ObjectName)+'\n'+str(s1.Object.Placement.Base)+'\n'+str(s1.Object.Placement.Rotation)+'\n')        
         outfile.write(make_string(s2.ObjectName)+'\n'+str(s2.Object.Placement.Base)+'\n'+str(s2.Object.Placement.Rotation)+'\n')        
    constraints = [ obj for obj in FreeCAD.ActiveDocument.Objects if 'ConstraintInfo' in obj.Content ]
    #print constraints
    if len(constraints) > 0:
         constraintFile = os.path.join( GuiPath , 'constraintFile.txt')
         if os.path.exists(constraintFile):
             with open(constraintFile, 'a') as outfile:
                 lastConstraintAdded = constraints[-1]
                 outfile.write(make_string(lastConstraintAdded.Name)+'\n')

    c.purgeTouched()
    if callSolveConstraints:
        c.Proxy.callSolveConstraints()  
        repair_tree_view()
    #FreeCADGui.Selection.clearSelection()
    #FreeCADGui.Selection.addSelection(c)
    return c
    

selection_text = '''Selectionner des aretes ou des faces circulaires'''

class CircularEdgeConstraintCommand:
    def Activated(self):
        selection = FreeCADGui.Selection.getSelectionEx()
        if len(selection) == 2:
            parseSelection( selection )
        else:
            FreeCADGui.Selection.clearSelection()
            ConstraintSelectionObserver( 
                CircularEdgeSelectionGate(), 
                parseSelection,
                taskDialog_title ='ajouter une contrainte de contour circulaire', 
                taskDialog_iconPath = self.GetResources()['Pixmap'], 
                taskDialog_text = selection_text
                )

    def GetResources(self): 
        return {
            'Pixmap' : ':/assembly2/icons/circularEdgeConstraint.svg' , 
            'MenuText': 'Ajouter une contrainte de contour circulaire', 
            'ToolTip': 'Ajouter une contrainte de contour circulaire entre deux objets'
            } 

FreeCADGui.addCommand('addCircularEdgeConstraint', CircularEdgeConstraintCommand())


class RedefineCircularEdgeConstraintCommand:
    def Activated(self):
        self.constObject = FreeCADGui.Selection.getSelectionEx()[0].Object
        debugPrint(3,'redefining %s' % self.constObject.Name)
        FreeCADGui.Selection.clearSelection()
        ConstraintSelectionObserver( 
                CircularEdgeSelectionGate(), 
                self.UpdateConstraint,
                taskDialog_title ='redefinir une contrainte de contour circulaire', 
                taskDialog_iconPath = ':/assembly2/icons/circularEdgeConstraint.svg', 
                taskDialog_text = selection_text
                )

    def UpdateConstraint(self, selection):
        parseSelection( selection, self.constObject)

    def GetResources(self): 
        return { 'MenuText': 'Redefinir' } 
FreeCADGui.addCommand('redefineCircularEdgeConstraint', RedefineCircularEdgeConstraintCommand())


class FlipLastConstraintsDirectionCommand:
    def Activated(self):
        constraints = [ obj for obj in FreeCAD.ActiveDocument.Objects 
                        if 'ConstraintInfo' in obj.Content ]
        if len(constraints) == 0:
            QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Commande abandonnee", 'Flip annule car aucune contrainte assembly2 dans le document actif.')
            return
        lastConstraintAdded = constraints[-1]
        if hasattr( lastConstraintAdded, 'directionConstraint' ):
            if lastConstraintAdded.directionConstraint == "none":
                QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Commande abandonnee", 'Flip annule puisque la direction de la derniere contrainte est desactivee')
                return
            if lastConstraintAdded.directionConstraint == "aligne":
                lastConstraintAdded.directionConstraint = "oppose"
            else:
                lastConstraintAdded.directionConstraint = "aligne"
        elif hasattr( lastConstraintAdded, 'angle' ):
            if lastConstraintAdded.angle.Value <= 0:
                lastConstraintAdded.angle = lastConstraintAdded.angle.Value + 180.0
            else:
                lastConstraintAdded.angle = lastConstraintAdded.angle.Value - 180.0
        else:
            QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Commande abandonnee", 'Retourner annule puisque la derniere contrainte ajoutee n a pas de direction ou d attribut d angle.')
            return
        FreeCAD.ActiveDocument.recompute()

    def GetResources(self): 
        return {
            'Pixmap' : ':/assembly2/icons/flipConstraint.svg' , 
            'MenuText': "Retourner la derniere direction de la contrainte", 
            'ToolTip': 'Retourne la direction de la derniere contrainte ajoutee'
            } 

FreeCADGui.addCommand('flipLastConstraintsDirection', FlipLastConstraintsDirectionCommand())



class LockRotationOfLastConstraintAddedCommand:
    def Activated(self):
        constraints = [ obj for obj in FreeCAD.ActiveDocument.Objects 
                        if 'ConstraintInfo' in obj.Content ]
        if len(constraints) == 0:
            QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Commande abandonnee", 'Set LockRotation = True abandonne car aucune contrainte assembly2 dans le document actif.')
            return
        lastConstraintAdded = constraints[-1]
        if hasattr( lastConstraintAdded, 'lockRotation' ):
            if not lastConstraintAdded.lockRotation:
                lastConstraintAdded.lockRotation = True
                FreeCAD.ActiveDocument.recompute()
            else:
                QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Information", 'Last constraints LockRotation attribute already set to True.')
        else:
            QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Command Aborted", 'Set LockRotation=True aborted since the last constraint added does not the LockRotation attribute.')
            return

    def GetResources(self): 
        return {
            'Pixmap' : ':/assembly2/icons/lockRotation.svg' , 
            'MenuText': "Definissez lockRotation-> True pour la derniere contrainte ajoutee", 
            'ToolTip': 'Definissez lockRotation-> True pour la derniere contrainte ajoutee'
            } 

FreeCADGui.addCommand('lockLastConstraintsRotation', LockRotationOfLastConstraintAddedCommand())
