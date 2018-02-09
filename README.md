FreeCAD_assembly2 Traduit en français
======================================

Établi d'assemblage pour FreeCAD v0.15, 0.16 et 0.17 avec support pour l'importation de pièces à partir de fichiers externes.
Bien que le programmeur original du workbench (hamish) ne soit plus actif
cet atelier est toujours maintenu aussi bon que possible.
Ne hésitez pas à poster des problèmes et tirer des demandes.
Assembly2 requiert numpy pour être installé (fourni avec FreeCAD depuis 0.15.4671).
Merci à Maurice (easyw-fc) assembly2 fonctionnera avec les fichiers de FreeCAD 0.17.


Linux Installation Instructions
-------------------------------

Pour Ubuntu (Linux Mint), nous recommandons d'ajouter la communauté ppa à votre logiciel système
ressources et installer via le gestionnaire de paquets sysnaptic l'addon de votre goût.
Reportez-vous ici pour plus d'informations:
https://launchpad.net/~freecad-community/+archive/ubuntu/ppa

On other Linux distros you may try to install manually via BASH and git:

```bash
$ sudo apt-get install git python-numpy python-pyside
$ mkdir ~/.FreeCAD/Mod
$ cd ~/.FreeCAD/Mod
$ git clone https://github.com/hamish2014/FreeCAD_assembly2.git
```

Once installed, use git to easily update to the latest version:

```bash
$ cd ~/.FreeCAD/Mod/FreeCAD_assembly2
$ git pull
$ rm *.pyc
```

Windows Installation Instructions
---------------------------------

Please use the FreeCAD-Addons-Installer provided here:
https://github.com/FreeCAD/FreeCAD-addons

For more in-depth information refer to the corresponding tutorial on the FreeCAD-Homepage:
http://www.freecadweb.org/wiki/index.php?title=How_to_install_additional_workbenches

Mac Installation Instructions
-----------------------------

* download the git repository as ZIP
* assuming FreeCAD is installed in "/Applications/FreeCAD/v 0.15", go to "/Applications/FreeCAD/v 0.15" in the Browser, and select FreeCAD.app
* right-click and select "Show Package Contents", a new window will appear with a folder named "Contents"
* single-click on the folder "Contents" and select the folder "Mod"
* in the folder "Mod" create a new folder named "assembly2"
* unzip downloaded repository in the folder "Contents/Mod/assembly2"
(Thanks piffpoof)


For more in-depth information refer to the corresponding tutorial on the FreeCAD-Homepage:
http://www.freecadweb.org/wiki/index.php?title=How_to_install_additional_workbenches

Wiki
----

For instructions on usage of the workbench refer to the wiki
[link on top of the page](https://github.com/hamish2014/FreeCAD_assembly2/wiki).
