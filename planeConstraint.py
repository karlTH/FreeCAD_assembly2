from assembly2lib import *
from lib3D import *
from pivy import coin
from PySide import QtGui

__dir2__ = os.path.dirname(__file__)
GuiPath = os.path.join( __dir2__, 'Gui' )
class PlaneSelectionGate:
     def allow(self, doc, obj, sub):
          return planeSelected( SelectionExObject(doc, obj, sub) )

class PlaneSelectionGate2:
     def allow(self, doc, obj, sub):
          s2 = SelectionExObject(doc, obj, sub)
          return planeSelected(s2) or vertexSelected(s2)

def promt_user_for_axis_for_constraint_label():
     preferences = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Assembly2")
     return preferences.GetBool('promtUserForAxisConstraintLabel', False)
     

def parseSelection(selection, objectToUpdate=None):
     validSelection = False
     if len(selection) == 2:
          s1, s2 = selection
          if s1.ObjectName != s2.ObjectName:
               if not planeSelected(s1):
                    s2, s1 = s1, s2
               if planeSelected(s1) and (planeSelected(s2) or vertexSelected(s2)):
                    validSelection = True
                    cParms = [ [s1.ObjectName, s1.SubElementNames[0], s1.Object.Label ],
                               [s2.ObjectName, s2.SubElementNames[0], s2.Object.Label ] ]
     if not validSelection:
          msg = '''La contrainte de plan necessite une selection de

- 2 plans, ou
- 1 plan and 1 sommet 

Selection faite:
%s'''  % printSelection(selection)
          QtGui.QMessageBox.information(  QtGui.qApp.activeWindow(), "Incorrect Usage", msg)
          return 

     if objectToUpdate is None:
          if promt_user_for_axis_for_constraint_label():
               extraText, extraOk = QtGui.QInputDialog.getText(QtGui.qApp.activeWindow(), "Axis", "Axis for constraint Label", QtGui.QLineEdit.Normal, "0")
               if not extraOk:
                    return
          else:
               extraText = ''
          cName = findUnusedObjectName('planeConstraint')
          debugPrint(2, "creating %s" % cName )
          c = FreeCAD.ActiveDocument.addObject("App::FeaturePython", cName)
          c.addProperty("App::PropertyString","Type","ConstraintInfo").Type = 'plane'
          c.addProperty("App::PropertyString","Object1","ConstraintInfo").Object1 = cParms[0][0]
          c.addProperty("App::PropertyString","SubElement1","ConstraintInfo").SubElement1 = cParms[0][1]
          c.addProperty("App::PropertyString","Object2","ConstraintInfo").Object2 = cParms[1][0]
          c.addProperty("App::PropertyString","SubElement2","ConstraintInfo").SubElement2 = cParms[1][1]
          c.addProperty('App::PropertyDistance','offset',"ConstraintInfo")
     
          c.addProperty("App::PropertyEnumeration","directionConstraint", "ConstraintInfo")
          c.directionConstraint = ["none","aligned","opposed"]

          c.setEditorMode('Type',1)
          for prop in ["Object1","Object2","SubElement1","SubElement2"]:
               c.setEditorMode(prop, 1) 
          c.Proxy = ConstraintObjectProxy()
          c.ViewObject.Proxy = ConstraintViewProviderProxy( c, ':/assembly2/icons/planeConstraint.svg', True, cParms[1][2], cParms[0][2], extraText) 
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
     c.Proxy.callSolveConstraints()
     repair_tree_view()
         

selection_text = '''Selection 1 options:
  - plan
Selection 2 options:
  - plan
  - sommet '''

class PlaneConstraintCommand:
     def Activated(self):
          selection = FreeCADGui.Selection.getSelectionEx()
          sel = FreeCADGui.Selection.getSelection()
          if len(selection) == 2:
               parseSelection( selection )
          else:
               FreeCADGui.Selection.clearSelection()
               ConstraintSelectionObserver( 
                    PlaneSelectionGate(), 
                    parseSelection, 
                    taskDialog_title ='add plane constraint', 
                    taskDialog_iconPath = self.GetResources()['Pixmap'], 
                    taskDialog_text = selection_text,
                    secondSelectionGate = PlaneSelectionGate2() )
               
     def GetResources(self): 
          return {
               'Pixmap' : ':/assembly2/icons/planeConstraint.svg', 
               'MenuText': 'Ajouter une contrainte de plan', 
               'ToolTip': 'Ajouter une contrainte de plan entre deux objets'
               } 

FreeCADGui.addCommand('addPlaneConstraint', PlaneConstraintCommand())


class RedefineConstraintCommand:
    def Activated(self):
        self.constObject = FreeCADGui.Selection.getSelectionEx()[0].Object
        debugPrint(3,'redefining %s' % self.constObject.Name)
        FreeCADGui.Selection.clearSelection()
        ConstraintSelectionObserver( 
                    PlaneSelectionGate(), 
                    self.UpdateConstraint, 
                    taskDialog_title ='Ajouter une contrainte de plan', 
                    taskDialog_iconPath = ':/assembly2/icons/planeConstraint.svg', 
                    taskDialog_text = selection_text,
                    secondSelectionGate = PlaneSelectionGate2() )

    def UpdateConstraint(self, selection):
        parseSelection( selection, self.constObject)

    def GetResources(self): 
        return { 'MenuText': u'Red\xE9finir'.encode("utf-8") } 
FreeCADGui.addCommand('redefinePlaneConstraint', RedefineConstraintCommand())
