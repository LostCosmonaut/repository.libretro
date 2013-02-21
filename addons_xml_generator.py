# *
# *  Copyright (C) 2012-2013 Garrett Brown
# *  Copyright (C) 2010      j48antialias
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *  Based on code by j48antialias:
# *  https://anarchintosh-projects.googlecode.com/files/addons_xml_generator.py

""" addons.xml generator """

import os
import sys
import shutil
import xml.etree.ElementTree as ET
import zipfile

try:
    import md5
except ImportError:
    import hashlib

# Compatibility with 3.0, 3.1 and 3.2 not supporting u"" literals
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x

class Addon:
    """
        Representation of an addon. Encompases addon.xml, changelog.txt,
        icon.png, fanart.jpg, and all other files. Output is an archive, the
        changelog at that version, an md5 hash of the archive, and an updated
        icon.png and fanart.png if changed.
    """
    def __init__(self, id):
        self.isaddon = False
        self.addon_xml = ''
        self.version = '1.0.0'
        self.changelog = False
        self.icon = False
        self.fanart = False
        self.files = []
        
        files = os.listdir(id)
        if 'addon.xml' in files:
            self.isaddon = True
            f = open(os.path.join(id, 'addon.xml'), 'r')
            xml_lines = f.read().splitlines()
            for line in xml_lines:
                # skip encoding format line
                if ( line.find( "<?xml" ) >= 0 ): continue
                # add line
                if sys.version < '3':
                    self.addon_xml += unicode( line.rstrip() + "\n", "UTF-8" )
                else:
                    self.addon_xml += line.rstrip() + "\n"
            f.close()
            
            # Now extract the version
            tree = ET.parse(os.path.join(id, 'addon.xml'))
            root = tree.getroot()
            self.version = root.attrib['version']
        else:
            return
        if 'changelog.txt' in files:
            self.changelog = True
        if 'icon.png' in files:
            self.icon = True
        if 'fanart.jpg' in files:
            self.fanart = True
        self.files = files


class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
    """
    def __init__( self ):
        # addon list
        addons = os.listdir(".")
        # final addons text
        addons_xml = u("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n")
        # loop through and add each addons addon.xml file
        for id in addons:
                #try:
                # skip any file or .svn folder or .git folder (or, for this repo, the release folder)
                if ( not os.path.isdir( id ) or id == ".svn" or id == ".git" or id == "release" ): continue
                # create Addon object
                addon = Addon(id)
                if ( not addon.isaddon ): continue
                addons_xml += addon.addon_xml.rstrip() + "\n\n"
                
                if not os.path.exists(os.path.join('release', id)):
                    os.makedirs(os.path.join('release', id))
                
                # Only copy new files if the version changed and the zip doesn't exist
                zipname = os.path.join('release', id, '%s-%s.zip' % (id, addon.version))
                with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as myzip:
                    for file in addon.files:
                        myzip.write(os.path.join(id, file))
                if addon.changelog:
                    old = os.path.join(id, 'changelog.txt')
                    new = os.path.join('release', id, 'changelog-%s.txt' % addon.version)
                    shutil.copy(old, new)
                if addon.icon:
                    old = os.path.join(id, 'icon.png')
                    new = os.path.join('release', id, 'icon.png')
                    shutil.copy(old, new)
                if addon.fanart:
                    old = os.path.join(id, 'fanart.jpg')
                    new = os.path.join('release', id, 'fanart.jpg')
                    shutil.copy(old, new)
                
                
                
                # create a new md5 hash
                self.make_md5_file(zipname)
                
                
                #try:
                #import md5
                #m = md5.new( open( zipname, 'rb' ).read() ).hexdigest()
                #except ImportError:
                #import hashlib
                #m = hashlib.md5( open( zipname, 'rb' ).read() ).hexdigest()
                
                # save file
                #try:
                #self._save_file( m, file=("%s.md5" % zipname) )
                #except Exception as e:
                # oops
                #print("An error occurred creating %s.md5 file!\n%s" % (zipname, e))
                
                #except Exception as e:
                # missing or poorly formatted addon.xml
                #print("Excluding %s for %s" % ( os.path.join(id, 'addon.xml'), e ))
        
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u("\n</addons>\n")
        try:
            open( 'addons.xml', 'wt', encoding='UTF-8' ).write( addons_xml )
        except TypeError:
            open( 'addons.xml', 'wb' ).write( addons_xml )
        
        self.make_md5_file('addons.xml')
        
        print("Finished updating addons xml and md5 files")
    
    def make_md5_file(self, file):
        try:
            m = hashlib.md5( open( file, 'rb' ).read() ).hexdigest()
            open( "%s.md5" % file, 'wt', encoding='UTF-8' ).write( m )
        except NameError:
            m = md5.new( open( file, 'rb' ).read() ).hexdigest()
            open( "%s.md5" % file, 'wb' ).write( m )


if ( __name__ == "__main__" ):
    # start
    Generator()