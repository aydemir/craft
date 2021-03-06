import abc
import os
import platform

import sys

from CraftOS.OsDetection import OsDetection


class OsUtilsBase(OsDetection, metaclass=abc.ABCMeta):
    @abc.abstractstaticmethod
    def rm(path, force=False):
        """ Removes a file"""
        pass

    @abc.abstractstaticmethod
    def rmDir(path, force=False):
        """ Removes a file"""
        pass

    @abc.abstractstaticmethod
    def getFileAttributes(path):
        """ Returns the attributes"""
        pass

    @abc.abstractstaticmethod
    def removeReadOnlyAttribute(path):
        """ Removes the readonly flag"""
        pass

    def setConsoleTitle(title):
        """ Set the console title """
        return True

    @staticmethod
    def supportsSymlinks() -> bool:
        return True
