import info
from CraftConfig import *
from CraftOS.osutils import OsUtils

class subinfo( info.infoclass ):
    def setTargets( self ):
        self.versionInfo.setDefaultValues( )

        self.shortDescription = "Konqueror"
        
    def setDependencies( self ):
        self.runtimeDependencies["virtual/base"] = "default"
        self.buildDependencies["frameworks/extra-cmake-modules"] = "master"
        self.runtimeDependencies["libs/qtbase"] = "default"
        self.runtimeDependencies["frameworks/kdelibs4support"] = "default"
        self.runtimeDependencies["frameworks/karchive"] = "default"
        self.runtimeDependencies["frameworks/kcrash"] = "default"
        self.runtimeDependencies["frameworks/kparts"] = "default"
        self.runtimeDependencies["frameworks/kcmutils"] = "default"
        self.runtimeDependencies["frameworks/kdoctools"] = "default"
        self.runtimeDependencies['libs/qtwebengine'] = 'default'
        
from Package.CMakePackageBase import *

class Package( CMakePackageBase ):
    def __init__( self ):
        CMakePackageBase.__init__( self )