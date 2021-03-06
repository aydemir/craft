#
# copyright (c) 2010-2011 Patrick Spendrin <ps_ml@gmx.de>
# copyright (c) 2010 Andre Heinecke <aheinecke@intevation.de> (code taken from the kdepim-ce-package.py)
#
import fileinput
import shutil
import types

from Packager.PackagerBase import *
from Blueprints.CraftDependencyPackage import DependencyType, CraftDependencyPackage
from Blueprints.CraftPackageObject import *


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def toRegExp(fname, targetName) -> re:
    """ Read regular expressions from fname """
    assert os.path.isabs(fname)

    if not os.path.isfile(fname):
        craftDebug.log.critical("%s not found at: %s" % (targetName.capitalize(), os.path.abspath(fname)))
    regex = "("
    for line in fileinput.input(fname):
        # Cleanup white spaces / line endings
        line = line.splitlines()
        line = line[0].rstrip()
        if line.startswith("#") or len(line) == 0:
            continue
        try:
            tmp = "^%s$" % line
            regex += "%s|" % tmp
            re.compile(tmp, re.IGNORECASE)  # for debug
            craftDebug.log.debug("%s added to %s as %s" % (line, targetName, tmp))
        except re.error:
            craftDebug.log.critical("%s is not a valid regexp" % tmp)
    return re.compile("%s)" % regex[:-2], re.IGNORECASE)


class PackagerLists(object):
    """ This class provides some staticmethods that can be used as pre defined black or whitelists """

    @staticmethod
    def runtimeBlacklist():
        return os.path.join(THIS_DIR, "applications_blacklist.txt")

    @staticmethod
    def defaultWhitelist():
        return [re.compile(".*")]

    @staticmethod
    def defaultBlacklist():
        return [toRegExp(PackagerLists.runtimeBlacklist(), "blacklist")]


class CollectionPackagerBase(PackagerBase):
    @InitGuard.init_once
    def __init__(self, whitelists=None, blacklists=None):
        PackagerBase.__init__(self)
        if not whitelists:
            whitelists = [PackagerLists.defaultWhitelist]
        if not blacklists:
            blacklists = [PackagerLists.defaultBlacklist]
        if not self.whitelist_file:
            self.whitelist_file = whitelists
        if not self.blacklist_file:
            self.blacklist_file = blacklists
        self._whitelist = []
        self._blacklist = []
        self.scriptname = None
        self.deployQt = True

    @property
    def whitelist(self):
        if not self._whitelist:
            for entry in self.whitelist_file:
                craftDebug.log.debug("reading whitelist: %s" % entry)
                if isinstance(entry, types.FunctionType) or isinstance(entry, types.MethodType):
                    for line in entry():
                        self._whitelist.append(line)
                else:
                    self.read_whitelist(entry)
        return self._whitelist

    @property
    def blacklist(self):
        if not self._blacklist:
            for entry in self.blacklist_file:
                craftDebug.log.debug("reading blacklist: %s" % entry)
                if isinstance(entry, types.FunctionType) or isinstance(entry, types.MethodType):
                    if entry == PackagerLists.runtimeBlacklist:
                        craftDebug.log.warn("Compat mode for PackagerLists.runtimeBlacklist -- please just use self.blacklist_file.append(\"myblacklist.txt\") instead of self.blacklist_file = [...]")
                        self.read_blacklist(entry())
                        continue

                    for line in entry():
                        self._blacklist.append(line)
                else:
                    self.read_blacklist(entry)
        return self._blacklist

    def __imageDirPattern(self, package, buildTarget):
        """ return base directory name for package related image directory """
        directory = "image"

        if package.subinfo.options.useBuildType == True:
            directory += '-' + package.buildType()
        directory += '-' + buildTarget
        return directory

    def __getImageDirectories(self):
        """ return the image directories where the files are stored """
        imageDirs = []
        depList = CraftDependencyPackage(self.package).getDependencies(depType=DependencyType.Runtime,
                                                                       ignoredPackages=self.ignoredPackages)

        for x in depList:
            if x.isVirtualPackage():
                craftDebug.log.debug(f"Ignoring package b/c it is virtual: {x}")
                continue

            _package = x.instance

            imageDirs.append((x.instance.imageDir(), x.subinfo.options.package.disableStriping))
            # this loop collects the files from all image directories
            craftDebug.log.debug(f"__getImageDirectories: package: {x}, version: {x.version}")

        if craftSettings.getboolean("QtSDK", "Enabled", False) and self.deployQt and craftSettings.getboolean("QtSDK",
                                                                                                              "PackageQtSDK",
                                                                                                              True):
            imageDirs.append((os.path.join(craftSettings.get("QtSDK", "Path"), craftSettings.get("QtSDK", "Version"),
                                           craftSettings.get("QtSDK", "Compiler")), False))

        return imageDirs

    def read_whitelist(self, fname):
        if not os.path.isabs(fname):
            fname = os.path.join(self.packageDir(), fname)
        """ Read regular expressions from fname """
        self._whitelist.append(toRegExp(fname, "whitelist"))

    def read_blacklist(self, fname):
        if not os.path.isabs(fname):
            fname = os.path.join(self.packageDir(), fname)
        """ Read regular expressions from fname """
        self._blacklist.append(toRegExp(fname, "blacklist"))

    def whitelisted(self, pathname):
        """ return True if pathname is included in the pattern, and False if not """
        for pattern in self.whitelist:
            if pattern.search(pathname):
                return True
        return False

    def blacklisted(self, filename):
        """ return False if file is not blacklisted, and True if it is blacklisted """
        for pattern in self.blacklist:
            if pattern.search(filename):
                return True
        return False

    def traverse(self, directory, whitelist=lambda f: True, blacklist=lambda g: False):
        """
            Traverse through a directory tree and return every
            filename that the function whitelist returns as true and
            which do not match blacklist entries
        """
        if blacklist(directory):
            return
        dirs = [directory]
        while dirs:
            path = dirs.pop()
            for f in os.listdir(path):
                f = os.path.join(path, f)
                z = f.replace(directory + os.sep, "")
                if blacklist(z):
                    continue
                if os.path.isdir(f):
                    dirs.append(f)
                elif os.path.isfile(f) and whitelist(z):
                    yield f

    def copyFiles(self, srcDir, destDir, strip):
        """
            Copy the binaries for the Package from srcDir to the imageDir
            directory
        """
        utils.createDir(destDir)
        craftDebug.log.debug("Copying %s -> %s" % (srcDir, destDir))
        uniquebasenames = []
        self.unique_names = []
        duplicates = []

        for entry in self.traverse(srcDir, self.whitelisted, self.blacklisted):
            if os.path.basename(entry) in uniquebasenames:
                craftDebug.log.debug("Found duplicate filename: %s" % os.path.basename(entry))
                duplicates.append(entry)
            else:
                self.unique_names.append(entry)
                uniquebasenames.append(os.path.basename(entry))

        for entry in self.unique_names:
            entry_target = entry.replace(srcDir, os.path.join(destDir + os.path.sep))
            if not os.path.exists(os.path.dirname(entry_target)):
                utils.createDir(os.path.dirname(entry_target))
            shutil.copy(entry, entry_target)
            craftDebug.log.debug("Copied %s to %s" % (entry, entry_target))
            if not strip and (entry_target.endswith(".dll") or entry_target.endswith(".exe")):
                self.strip(entry_target)
        for entry in duplicates:
            entry_target = entry.replace(srcDir, destDir + os.path.sep)
            if not os.path.exists(os.path.dirname(entry_target)):
                utils.createDir(os.path.dirname(entry_target))
            shutil.copy(entry, entry_target)
            craftDebug.log.debug("Copied %s to %s" % (entry, entry_target))
            if not strip and (entry_target.endswith(".dll") or entry_target.endswith(".exe")):
                self.strip(entry_target)

    def internalCreatePackage(self):
        """ create a package """

        archiveDir = self.archiveDir()

        craftDebug.log.debug("cleaning package dir: %s" % archiveDir)
        utils.cleanDirectory(archiveDir)
        for directory, strip in self.__getImageDirectories():
            imageDir = archiveDir
            if os.path.exists(directory):
                self.copyFiles(directory, imageDir, strip)
            else:
                craftDebug.log.critical("image directory %s does not exist!" % directory)

        if not os.path.exists(archiveDir):
            os.makedirs(archiveDir)

        if self.subinfo.options.package.movePluginsToBin:
            # Qt expects plugins and qml files below bin, on the target sytsem
            binPath = os.path.join(archiveDir, "bin")
            for path in [os.path.join(archiveDir, "plugins"), os.path.join(archiveDir, "qml")]:
                if os.path.isdir(path):
                    utils.mergeTree(path, binPath)

        return True

    def preArchive(self):
        return True
