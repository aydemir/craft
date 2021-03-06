#
# copyright (c) 2009 Ralf Habacker <ralf.habacker@freenet.de>
#

from Source.ArchiveSource import ArchiveSource
from Source.GitSource import GitSource
from Source.HgSource import HgSource

from Source.SourceBase import *
from Source.SvnSource import SvnSource


class MultiSource(SourceBase):
    """ provides multi source type api """

    def __init__(self):
        SourceBase.__init__(self)
        craftDebug.trace("MultiSource __init__")

        self.source = None
        if self.subinfo.hasSvnTarget():
            url = self.subinfo.svnTarget()
            sourceType = utils.getVCSType(url)
            if sourceType == "svn":
                self.source = SvnSource
            elif sourceType == "hg":
                self.source = HgSource
            elif sourceType == "git":
                self.source = GitSource
        elif self.subinfo.hasTarget():
            self.source = ArchiveSource

        if self.source:
            self.__class__.__bases__ += (self.source,)
            self.source.__init__(self)

    # todo: find a more general way to publish all members
    def fetch(self):
        craftDebug.trace("MultiSource fetch")
        return self.source.fetch(self)

    def checkDigest(self):
        craftDebug.trace("MultiSource checkDigest")
        return self.source.checkDigest(self)

    def unpack(self):
        craftDebug.trace("MultiSource unpack")
        return self.source.unpack(self)

    def localFileNames(self):
        craftDebug.trace("MultiSource localFileNames")
        return self.source.localFileNames(self)

    def checkoutDir(self, index=0):
        craftDebug.trace("MultiSource checkoutDir")
        return self.source.checkoutDir(self, index=index)

    def sourceDir(self):
        craftDebug.trace("MultiSource sourceDir")
        return CraftShortPath(self.source.sourceDir(self)).conditionalShortPath(self.subinfo.options.needsShortPath)

    def repositoryUrl(self, index=0):
        craftDebug.trace("MultiSource repositoryUrl")
        return self.source.repositoryUrl(self, index)

    def repositoryUrlCount(self):
        craftDebug.trace("MultiSource repositoryUrlCount")
        return self.source.repositoryUrlCount(self)

    def applyPatches(self):
        craftDebug.trace("MultiSource applyPatches")
        return self.source.applyPatches(self)

    def createPatch(self):
        craftDebug.trace("MultiSource createPatch")
        return self.source.createPatch(self)

    def getUrls(self):
        craftDebug.trace("MultiSource getUrls")
        return self.source.getUrls(self)

    def sourceVersion(self):
        craftDebug.trace("MultiSource sourceVersion")
        return self.source.sourceVersion(self)

    def sourceRevision(self):
        craftDebug.trace("MultiSource sourceVersion")
        return self.source.sourceRevision(self)

    def printSourceVersion(self):
        craftDebug.trace("MultiSource printSourceVersion")
        return self.source.printSourceVersion(self)
