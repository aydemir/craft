import info
import shutil
import os

class subinfo(info.infoclass):
    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'

    def setTargets( self ):
        for ver in ['1.75.2', '1.78.0']:
            self.targets[ ver ] = 'http://downloads.sourceforge.net/docbook/docbook-xsl-' + ver + '.tar.bz2'
        self.targetDigests['1.75.2'] = 'cd146012c07f3c2c79c1cd927ad1faf5bee6cc74'
        self.targetDigests['1.78.0'] = '39a62791e7c1479e22d13d12a9ecbb2273d66229'
        self.shortDescription = "document translation defintions for docbook format"
        self.options.package.withCompiler = False
        self.options.package.packSources = False
        self.defaultTarget = '1.75.2'

from Package.BinaryPackageBase import *

class Package(BinaryPackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        BinaryPackageBase.__init__( self )
        self.subinfo.options.install.installPath = 'share/xml/docbook'

    def unpack( self ):
        """rename the directory here"""
        if not BinaryPackageBase.unpack(self):
            return False
        os.rename(os.path.join(self.installDir(), os.path.basename(self.repositoryUrl()).replace(".tar.bz2", "")),
                  os.path.join(self.installDir(), "xsl-stylesheets-" + self.subinfo.buildTarget))
        return True

if __name__ == '__main__':
    Package().execute()
