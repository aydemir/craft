#
# copyright (c) 2010 Ralf Habacker <ralf.habacker@freenet.de>
#

"""@package provides simple makefile based build system without any configure step"""

from BuildSystem.BuildSystemBase import *


class MakeFileBuildSystem(BuildSystemBase):
    """ make file build support """

    def __init__(self):
        """constructor. configureOptions are added to the configure command line and makeOptions are added to the make command line"""
        BuildSystemBase.__init__(self, "makefile")

    def configure(self, dummyDefines=""):
        """implements configure step for cmake projects"""

        return True

    def make(self):
        """implements the make step for Makefile projects"""

        self.enterBuildDir()

        command = ' '.join([self.makeProgram, self.makeOptions()])

        return self.system(command, "make")

    def install(self):
        """install the target"""
        if not BuildSystemBase.install(self):
            return False

        self.enterBuildDir()
        command = "%s install DESTDIR=%s" % (self.makeProgram, self.installDir())
        self.system(command, "install")
        return True

    def unittest(self):
        """running make tests"""

        self.enterBuildDir()

        return self.system("%s test" % (self.makeProgram), "test")
