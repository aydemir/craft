# -*- coding: utf-8 -*-
import info
import utils
from Package.CMakePackageBase import *

class subinfo(info.infoclass):
    def setTargets( self ):
        for ver in [ '0.4.1' ]:
            self.targets[ ver ] = 'http://git.kolab.org/libkolab/snapshot/libkolab-' + ver + '.tar.gz'
            self.targetInstSrc[ ver ] = "libkolab-" + ver
        self.patchToApply['0.4.1'] = [("libkolab-fixes.diff", 1)]
        self.targetDigests['0.4.1'] = 'fd455fe6e4f8e3c34df1bcc3f83e8567981912ea'

        self.shortDescription = ''
        self.defaultTarget = '0.4.1'

    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'
        self.buildDependencies['win32libs/libkolabxml'] = 'default'

        # the following dependencies are dragged in by the static libkolabxml library
        self.dependencies['binary/xerces-c-bin'] = 'default'
        self.dependencies['win32libs/boost-system'] = 'default'
        self.dependencies['win32libs/boost-thread'] = 'default'

        # this is a real dependency of libkolab
        self.dependencies['kde/kdepimlibs'] = 'default'

class Package(CMakePackageBase):
    def __init__( self, **args ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )
        self.subinfo.options.configure.defines = "-DBUILD_TESTS=OFF"

if __name__ == '__main__':
    Package().execute()