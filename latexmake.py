#!/usr/bin/python

# ABOUT:
#	A python script I have been working on to make the Makefile for a generic
#	TeX document. It is probably similar to latexmk [1], but there is something
#	to be said for writing some things yourself!
#
# PUBLIC REPOSITORY:
#	https://github.com/pavdpr/latexmake
#
# SUGGESTED USE:
#	- Put the git repository on your machine (the location is /path/to/repo)
#	- In your path (type "echo $PATH" w/o quotes in terminal to see the locatons
#	of path. A further suggestion: add a folder to PATH that does not require root
#	access, e.g, ~/bin), make a link to this file:
#		cd /someplace/in/path
#		ln -s /path/to/repo/latexmake.py latexmake
#
# HISTORY:
#	2014-01-30: Paul Romanczyk
#	- Initial version (0.0.1)
#
#	2014-05-28: Paul Romanczyk
#	- Working on latexdiff stuff
#
# TODO:
#	- Fix ability to read in multiline package commands
#		+ Strip all newlines?
#	- Add in latexdiff support
#		+ use gitlatexdiff https://github.com/daverted/gitlatexdiff as an example
#	- Add in git support
#
# REQUIRED TOOLS:
#	make         http://www.gnu.org/software/make/
#
# OPTIONAL TOOLS:
#	git          http://git-scm.com
#	latex2rtf    http://latex2rtf.sourceforge.net
#	latexdiff    http://latexdiff.berlios.de
#	latexpand    http://www.ctan.org/pkg/latexpand
#	bibsort      http://ftp.math.utah.edu/pub/bibsort/
#
# LICENSE
# 	The MIT License (MIT)
#
#	Copyright 2014 Paul Romanczyk
#
# 	Permission is hereby granted, free of charge, to any person obtaining a copy
# 	of this software and associated documentation files (the "Software"), to
#	deal in the Software without restriction, including without limitation the
#	rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#	sell copies of the Software, and to permit persons to whom the Software is
#	furnished to do so, subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be included in
#	all copies or substantial portions of the Software.
#
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#	FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#	IN THE SOFTWARE.
#
# REFERENCES:
#	[1] http://users.phys.psu.edu/~collins/software/latexmk-jcc/ [2014-01-08]
#	[*] http://tex.stackexchange.com/questions/7770/file-extensions-of-latex-related-files
#
#


# import other packages
import os;          # for interacting with files and directories
import re;          # for parsing strings
import sys;         # for getting command-line input
import datetime;    # for adding date stamps
import platform;    # for determining if a mac to use open


# set the version number
latexmake_version_major = 0;
latexmake_version_minor = 0;
latexmake_version_revision = 3;


#================================================================================
#
#		Exception Classes
#
#================================================================================


#-------------------------------------------------------------------------------
class latexmake_invalidInput( RuntimeError ):
   def __init__( self, arg ):
      self.args = arg;
# class latexmake_invalidInput( RuntimeError )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_noInput( RuntimeError ):
   def __init__( self, arg ):
      self.args = arg;
# class latexmake_noInput( RuntimeError )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_invalidBasename( RuntimeError ):
   def __init__( self, arg ):
      self.args = arg;
# class latexmake_invalidBasename( RuntimeError )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_nonexistantFile( RuntimeError ):
   def __init__( self, arg ):
      self.args = arg;
# class latexmake_invalidBasename( RuntimeError )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_invalidArgument( RuntimeError ):
   def __init__( self, arg ):
      self.args = arg;
# class latexmake_invalidArgument( RuntimeError )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_invalidBracketOrder( RuntimeError ):
   def __init__( self, arg ):
      self.args = arg;
# class latexmake_invalidArgument( RuntimeError )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_makeDoesNotExist( RuntimeError ):
   def __init__( self, arg ):
      self.args = arg;
# class latexmake_makeDoesNotExist( RuntimeError )
#-------------------------------------------------------------------------------


#================================================================================
#
#		Debug
#
#================================================================================


#-------------------------------------------------------------------------------
def debug_writeFile( filename, content, info="" ):
	( filename, fileextension ) = os.path.splitext( filename );
	filename += "_" + "-".join( ( "-".join( str( \
		datetime.datetime.utcnow() ).split( " " ) ) ).split( ":" ) ) + \
		info + fileextension;

	fid = open( filename, "w" );
	fid.write( content );
	fid.close();
	return;
#fed debug_writeFile( filename, content )
#-------------------------------------------------------------------------------


#================================================================================
#
#		Executable testing code
#
#================================================================================


#-------------------------------------------------------------------------------
def is_exe( fpath ):
	# used to see if fpath is an executable
	# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
	return os.path.isfile( fpath ) and os.access( fpath, os.X_OK );
# fed is_exe( fpath )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def functionExists( program ):

	fpath, fname = os.path.split( program );
	if fpath:
		return is_exe( program );
	else:
		for path in os.environ[ "PATH" ].split( os.pathsep ):
			path = path.strip( '"' ); # TODO: see if I can use "\""
			exe_file = os.path.join( path, program );
			if is_exe( exe_file ):
				return True;

		return False;
# fed functionExists( program )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def which( program ):
	# a unix-like which
	# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python

	fpath, fname = os.path.split( program );
	if fpath:
		if is_exe( program ):
			return program;
	else:
		for path in os.environ[ "PATH" ].split( os.pathsep ):
			path = path.strip( '"' );
			exe_file = os.path.join( path, program );
			if is_exe( exe_file ):
				return exe_file;

	# program does not exist, return None
	return None;
# fed which( program )
#-------------------------------------------------------------------------------


#================================================================================
#
#		Output Messages
#
#================================================================================


#-------------------------------------------------------------------------------
def latexmake_usage():
	output = "latexmake [options] basefilename\n";
	output += "\t--tex=/path/to/tex compiler\n";
	output += "\t--bib=/path/to/bib compiler\n";
	#output += "\t--nooverwrite\t\t\tWill not overwrite a Makefile\n";
	return output
# fed latexmake_usage()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def latexmake_copyright():
	output = "latexmake\n";
	output += "\n\tCopyright 2014 Paul Romanczyk\n";
	return output
# fed latexmake_copyright()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def latexmake_version():
	output = \
	str( latexmake_version_major ) + "." + \
	str( latexmake_version_minor ) + "." + \
	str( latexmake_version_revision );
	return output;
# fed latexmake_version()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def latexmake_header():
	output  = "# Generated by latexmake v" + latexmake_version() + "\n";
	output += "# Created on " + str( datetime.datetime.utcnow() ) + " UTC\n";
	output += "# latexmake repository: https://github.com/pavdpr/latexmake\n";
	return output;
# fed latexmake_header()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def warning( message ):
	print message;
# fed warning( message );
#-------------------------------------------------------------------------------


#================================================================================
#
#		helper functions
#
#================================================================================

#-------------------------------------------------------------------------------
def unique( data ):
	# I do not think this can be solved with list comprehension
	output = [];
	for item in data:
		if item not in output:
			output.append( item );
	return output;

# fed unique( data )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def compliment( data, exclude ):
	return [ item for item in data if item not in exclude ];

# fed compliment( data, exclude )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def parseLongLines( line, lineLength, tabLength, numTabs, extra ):
	if numTabs < 0:
		numTabs = 0;

	maxLength = lineLength - numTabs * tabLength - 2;
	output = [];
	tmp = "";
	l = line.split();
	ct = 0;
	while len( l ) > 0:
		run = True;
		while ( run ):
			if len( tmp ) == 0:
				tmp = l[ 0 ];
				l = l[ 1: ];
				if len( l ) == 0:
					run = False;
			elif len( tmp + " " + l[ 0 ] ) > maxLength:
				run = False;
			else:
				tmp += ( " " + l[ 0 ] );
				l = l[ 1: ];
				if len( l ) == 0:
					run = False;

		output.append( tmp );
		tmp = "";
		if extra:
			# add room for double tab on second or higher lines
			ct = ct + 1;
			if ( ct == 1 ) and ( lineLength - 2 - ( numTabs + 1 ) * tabLength > 0 ):
				maxLength -= tabLength;

	return output;
# fed parseLongLines( line, maxLength )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def writeLongLines( fid, line, lineLength, tabLength, numTabs, extra ):
	lines = parseLongLines( line, lineLength, tabLength, numTabs, extra );
	if numTabs < 0:
		numTabs = 0;

	tabs = "";
	for i in range( 0, numTabs ):
		tabs += "\t";

	if not extra:
		for l in lines[ :-1 ]:
			fid.write( tabs + l + " \\\n" );
		fid.write( tabs + lines[ -1 ] + "\n" );
	else:
		fid.write( tabs + lines[0] + " \\\n" );
		tabs += "\t";
		for l in lines[ 1:-1 ]:
			fid.write( tabs + l + " \\\n" );
		fid.write( tabs + lines[ -1 ] + "\n" );
	return;
# fed parseLongLines( line, maxLength )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def parseEquals( s ):
	try:
		idx = s.find( "=" );
		if idx < 0:
			raise latexmake_invalidArgument( s );
		left = s[ :idx ];
		right = s[ idx+1: ];
	except latexmake_invalidArgument, e:
		raise latexmake_invalidArgument( e.args );
	else:
		return ( left, right );
# fed parseEquals( s )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findUnescaped( line, char ):
	idx = line.find( char );
	if idx > 0:
		if line[ idx - 1 ] == "\\":
			if idx < len( line ) - len( char ):
				# recursively look for the next char
				tmp = findUnescaped( line[ idx + len( char ): ], char );
				if tmp < 0:
					return tmp;
				else:
					return tmp + idx + len( char );
			else:
				return -1;
	# if idx == 0: cannot be escaped => return idx (=0)
	# if idx < 0: return idx (=-1)

	return idx;
# fed findNext( line, char )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def purifyListOfStrings( l, key ):
	return [ item for item in l if not re.search( key, item ) ];
# fed def purifyListOfStrings( l, key )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def parseDataInBraces( line, leftBrace, rightBrace ):
	try:
		output = [];
		lstack = [];

		lidx = findUnescaped( line, leftBrace );
		ridx = findUnescaped( line, rightBrace );

		# no braces
		if lidx < 0:
			return [];

		run = True;
		while run:

			if len( lstack ) == 0:
				if lidx < 0:
					if ridx < 0:
						run = False;
					else:
						message = "In string: '" + line + "':\n";
						message += "\tunbalanced " + leftBrace + rightBrace;
						raise latexmake_invalidBracketOrder( message );
				else:
					lstack.append( lidx );
					tmp = findUnescaped( line[ lidx+1:], leftBrace );
					if tmp < 0:
						lidx = -1;
					else:
						lidx += tmp + 1;
			elif lidx < ridx and lidx > 0:
				lstack.append( lidx );
				tmp = findUnescaped( line[ lidx+1:], leftBrace );
				if tmp < 0:
					lidx = -1;
				else:
					lidx += tmp + 1;
			elif ridx >= 0:
				if ( len( lstack  ) == 0 ):
					message = "In string: '" + line + "':\n";
					message += "\tunbalanced " + leftBrace + rightBrace;
					raise latexmake_invalidBracketOrder( message );
				elif lstack[-1] >= ridx:
					message = "In string: '" + line + "':\n";
					message += "\t'" + rightBrace + "' appears before '" + \
					leftBrace + "'";
					raise latexmake_invalidBracketOrder( message );

				output.append( line[ lstack.pop() + 1:ridx ] );
				tmp = findUnescaped( line[ ridx+1:], rightBrace );
				if tmp < 0:
					ridx = -1;
				else:
					ridx += tmp + 1;
			else:
				if findUnescaped( line[ ridx+1:], rightBrace ) < 0:
					run = False;
				else:
					message = "In string: '" + line + "':\n";
					message += "\tunbalanced " + leftBrace + rightBrace;
					raise latexmake_invalidBracketOrder( message );

		return output;
	except:
		print message
		raise;
# fed parseDataInBraces( line, leftBrace, rightBrace )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def parseDataInSquiglyBraces( line ):
	try:
		return parseDataInBraces( line, "{", "}" );
	except:
		raise;
# fed parseDataInSquiglyBraces( line )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def parseDataInSquareBraces( line ):
	try:
		return parseDataInBraces( line, "[", "]" );
	except:
		raise;
# fed parseDataInSquareBraces( line )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def parseDataInParentheses( line ):
	try:
		return parseDataInBraces( line, "(", ")" );
	except:
		raise;
# fed parseDataInParenthesies( line )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def parseDataInAngleBraces( line ):
	try:
		return parseDataInBraces( line, "<", ">" );
	except:
		raise;
# fed parseDataInAngleBraces( line )
#-------------------------------------------------------------------------------



#================================================================================
#
#		TeX file parsing
#
#================================================================================


#-------------------------------------------------------------------------------
def parseCommaSeparatedData( line ):
	tmp = line.split( "," );
	# trim whitespace
	return [ item.strip() for item in tmp ];
# fed parseCommaSeparatedData( line )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def prepareTeXfile( texFile, filename ):
	# filename is for debug purposes

	# remove newlines (escaped \ to prevent \\% from being excluded )
	texFile = re.sub( r"\\\\", "", texFile );

	# merge lines that end in a comment
	texFile = re.sub( r"(?<!\\)%.*", "", texFile );

	# recombine comma ended lines
	texFile = re.sub( r",\s*[\n\r]", ",", texFile );

	# todo?: remove whitespace at end of line.
	#	-> will probably just slow down code

	return texFile;
# fed prepareTeXfile( texFile, thisFilename )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findPackages( texFile, params, thisFileName ):
	# TODO: This does not work in cases like
	# \usepackage[sorting=ydnt,		% reverse sort by date
	# bibstyle=authoryear,			% use author year style (not sure how much this does w/o /cite{})
	# defernumbers=true,			%
	# maxnames=99,			 		% show up to 99 author names in the reference
	# firstinits=true, 				% use first initials
	# terseinits=false,				% period after initials
	# uniquename=init,				%
	# dashed=false,					%
	# uniquename=false,				%
	# doi=true,						% include doi where present
	# isbn=false,					% include isbn where present
	# useprefix=true,				%
	# natbib=true,					%
	# backend=biber]				% use biber on the backend
	# {biblatex}
	#
	# I probably need to abandon regular expressions
	#
	# TODO: also have this work with \requirepackage

	key = r"\\usepackage(\[.*\])?(\{.*\})";
	locs = re.findall( key, texFile );
	packages = [];
	for tmp in locs:
		line = tmp[ -1 ];
		for part in purifyListOfStrings( parseDataInSquiglyBraces( line ), \
				r"[\{\}]" ):
			p = parseCommaSeparatedData( part );
			packages += p;
			for package in p:
				# check to see if it is local
				params = findLocalStyFiles( package, params, thisFileName );
				if package == "biblatex":
					# TODO finish
					m = re.search( r"\\usepackage(\[.*\]?\{\s*biblatex\s*\})", \
						texFile );
					optionStrings = parseDataInSquareBraces( m.group() );
					for optionString in optionStrings:
						options = parseCommaSeparatedData( optionString );
						opts = [ parseEquals( option ) for option in options ];
						backend = "bibtex"; # default
						for opt in opts:
							if opt[ 0 ] == "backend":
								backend = opt[ 1 ];
						if functionExists( backend ):
							params[ "bib_engine" ] = backend.upper();
						else:
							warning( "The bibliography backend \"" + backend + \
								"\" cannot be found" );

				elif package == "epstopdf":
					if params[ "tex_engine" ] == "PDFLATEX":
						params[ "fig_extensions" ] += ".eps";

				elif package == "makeidx":
					params[ "make_index_in_default" ] = True;

				# elif package == "glossaries":
				# 	params[ "make_glossary_in_default" ] = True;

	# update the packages list in params
	params[ "packages" ] += packages;
	return params;
# fed findPackages( texFile, params )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findGraphicsPaths( texFile, params, thisFileName ):
	locs = re.findall( r"\\graphicspath\{(.*)\}", texFile );
	for line in locs:
		for part in purifyListOfStrings( parseDataInSquiglyBraces( line ), \
			r"[\{\}]" ):
			if os.path.isdir( part ) and os.path.exists( part ):
				# we are a valid path
				params[ "graphics_paths" ].append( os.path.abspath( part ) );
				if os.path.abspath( part ) not in params[ "sub_paths" ]:
					params[ "sub_paths" ].append( os.path.abspath( part ) );
			else:
				#TODO?: raise exception
				warning( "In \"" + thisFileName + "\": \"" + part + \
					"\" is not a valid graphicspath" );
	return params;
# fed findGraphicsPaths( texFile, params )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findGraphicsExtensions( texFile, params, thisFileName ):
	locs = re.findall( r"\\DeclareGraphicsExtensions\{(.*)\}", texFile );
	if not locs:
		return params;
	for item in locs:
		if parseDataInSquiglyBraces( item ):
			# residual squiglies
			item = parseDataInSquiglyBraces( item );
			params[ "fig_extensions" ] = parseCommaSeparatedData( item );
			#TODO: check to see if I can have a .jpg if the g.e. is just .eps
	return params;
# fed findGraphicsExtensions( texFile, params )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findFigures( texFile, params, thisFileName ):
	# TODO: also get pgf figures
	m = re.findall( r"\\includegraphics(\[.*\])?\s*(\{[\w\/ ]\})", texFile );
	if not m:
		return params;

	# figures = [ [ parseDataInSquiglyBraces( fig )[0]\
	# for fig in figTuple if fig ] for figTuple in m ]

	figures = [];
	for figTuple in m:
		for fig in figTuple:
			if fig:
				figures += parseDataInSquiglyBraces( fig );



	for fig in figures:
		# try to find possible figures without adding an extension
		posibleFigures = \
		[ os.path.abspath( os.path.join( pth, fig ) ) \
		for pth in params[ "graphics_paths" ] \
		if os.path.isfile( os.path.join( pth, fig ) ) ];

		# retry but append paths this time
		if not posibleFigures:
				posibleFigures = \
				[ os.path.abspath( os.path.join( pth, fig + ext ) ) \
				for pth in params[ "graphics_paths" ] \
				for ext in params[ "fig_extensions" ] \
				if os.path.isfile( os.path.join( pth, fig + ext ) )];

		if posibleFigures:
			params[ "fig_files" ].append( posibleFigures[ 0 ] );
		elif params[ "verbose" ]:
			warning( "Figure \"" + fig + "\" not found" );

	# print figures;
		# for part in purifyListOfStrings( parseDataInSquiglyBraces( line ), \
		# 	"\{\}" ):
		# 	figure = parseCommaSeparatedData( part );
		# 	figures += figure;
	return params;
# fed findFigures( texFile, params )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findSubTeXfiles( texFile, params, thisFileName ):
	key = r"\\(include|input)(\[.*\])?(\{[\w\/ ]*\})";
	locs = re.findall( key, texFile );
	files = [];
	for tmp in locs:
		line = tmp[ -1 ];
		for part in purifyListOfStrings( parseDataInSquiglyBraces( line ), \
		 	r"[\{\}]" ):
			p = parseCommaSeparatedData( part );
			for subfile in parseCommaSeparatedData( part ):
				f = None;
				if os.path.isfile( subfile ):
					f = os.path.abspath( subfile );

				elif os.path.isfile( subfile + ".tex" ):
					f = os.path.abspath( subfile + ".tex" );

				elif params[ "verbose" ]:
					#TODO?: raise exception
					warning( "In \"" + thisFileName + \
						"\" tex file Not Found: \"" + subfile + "\"" );

				if f:
					params[ "tex_files" ].append( f );
					( tmp, _ ) = os.path.split( f );
					tmp = os.path.abspath( tmp );
					if tmp not in params[ "sub_paths" ]:
						params[ "sub_paths" ].append( tmp );

					# parse the sub tex file
					params = parseLatexFile( f, params );




	return params;
# fed findSubTeXfiles( texFile, params )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findBibliographies( texFile, params, thisFileName ):
	if "biblatex" in params[ "packages" ]:
		key = r"\\addbibresource(\{.*\})";
	else:
		key = r"\\bibliography(\{.*\})";

	locs = re.findall( key, texFile );
	for loc in locs:
		parsedSquigly = parseDataInSquiglyBraces( loc );
		for dataInSquigly in parsedSquigly:
			bibs = parseCommaSeparatedData( dataInSquigly );
			for bib in bibs:
				if os.path.isfile( bib ):
					params[ "bib_files" ].append( os.path.abspath( bib ) );
				elif os.path.isfile( bib + ".bib" ):
					params[ "bib_files" ].append( os.path.abspath( bib + \
						".bib" ) );
				elif params[ "verbose" ]:
					#TODO?: raise exception
					warning( "In \"" + thisFileName + \
						"\" bib file Not Found: \"" + bib + "\"" );

	if ( locs ):
		params[ "make_bib_in_default" ] = True;

	return params;
# fed findBibliographies( texFile, params, thisFileName )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findGlossary( texFile, params, thisFileName ):
	if "glossaries" not in params[ "packages" ]:
		# if glossary package is not defined, we cannot have a glossary
		return params;

	key = re.compile( r"\\makeglossaries" );
	hasGloss = key.search( texFile );
	if hasGloss:
		params[ "make_glossary_in_default" ] = True;
	return params;
# fed findGlossary( texFile, params, thisFileName )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findLocalClsFiles( clsname, params, thisFileName ):
	# TODO: impliment
	# TODO: also look in texmfpath for non-standard cls files
	return params;
# fed findLocalClsFiles( clsname, params, thisFileName )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findLocalStyFiles( styname, params, thisFileName ):
	# TODO: also look in texmfpath for non-standard sty files
	for root, dirs, files in os.walk( params[ "basepath" ] ):
		if ".git" in dirs:
			dirs.remove( ".git" );
			# TODO: include other subfolder excludes

		f = None;
		# this is bad logic. files may be in the directory tree.

		if styname in files:
			f = os.path.abspath( styname );
		elif ( styname + ".sty" ) in files:
			f = os.path.abspath( styname + ".sty" );

		if f:
			params[ "sty_files" ].append( f );

			#parse the included local style file
			params = parseLatexFile( f, params )

	return params;
# fed findLocalStyFiles( styfilename, params, thisFileName )
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
def parseLatexFile( filename, params ):
	fid = open( filename, "r" );
	if fid < 0:
		raise latexmake_nonexistantFile( filename );

	texFile = fid.read();
	fid.close();

	# TODO: look for latexmk directives here

	# prepare the TeX file. (remove comments)
	texFile = prepareTeXfile( texFile, filename );

	# attempt to use existing code to read multiline \usepackages
	#texFile = " ".join(texFile.split("\n"))

	# search for packages
	params = findPackages( texFile, params, filename );

	# search for included tex files
	params = findSubTeXfiles( texFile, params, filename );

	# search for Graphics Extensions
	params = findGraphicsExtensions( texFile, params, filename );

	# find graphics paths
	params = findGraphicsPaths( texFile, params, filename );

	# search for figures
	params = findFigures( texFile, params, filename );

	# search for bibliographies
	params = findBibliographies( texFile, params, filename );

	# search to see if we are makeing a glossary
	params = findGlossary( texFile, params, filename );

	return params;

# fed parseLatexFile( file )
#-------------------------------------------------------------------------------


#================================================================================
#
#		Meat and Potatoes
#
#================================================================================


#-------------------------------------------------------------------------------
def latexmake_default_params():
	params = {};
	# options
	params[ "makediff" ] = True;
	params[ "verbose" ] = False;

	# tex command locations
	params[ "tex" ] = "tex";
	params[ "latex" ] = "latex";
	params[ "pdflatex" ] = "pdflatex";
	params[ "luatex" ] = "luatex";
	params[ "lualatex" ] = "lualatex";
	params[ "xelatex" ] = "xelatex";
	params[ "xetex" ] = "xelatex";
	params[ "bibtex" ] = "bibtex";
	params[ "biber" ] = "biber";
	params[ "dvips" ] = "dvips";
	params[ "ps2eps" ] = "ps2eps";
	params[ "pstopdf" ] = "pstopdf";
	params[ "epstopdf" ] = "epstopdf";
	params[ "makeglossaries" ] = "makeglossaries";
	params[ "makeindex" ] = "makeindex";
	params[ "tex_commands" ] = [ "tex", "latex", "pdflatex", "luatex", \
		"lualatex", "xelatex", "xelatex", "bibtex", "biber", "dvips", \
		"ps2eps", "pstopdf", "epstopdf", "makeglossaries", "makeindex", \
		"tex2rtf", "latex2rtf" ];

 	params[ "tex_engine" ] = "PDFLATEX";
	params[ "tex_options" ] = "--file-line-error --synctex=1"; #include synctex to help out TeXShop
	params[ "bib_engine" ] = "BIBTEX";
	params[ "idx_engine" ] = "MAKEINDEX";
	params[ "gls_engine" ] = "MAKEGLOSSARIES";
	params[ "make_bib_in_default" ] = False;
	params[ "make_index_in_default" ] = False;
	params[ "make_glossary_in_default" ] = False;
	params[ "basename" ] = "";
	params[ "basepath" ] = os.path.abspath( "." );
	params[ "tex_files" ] = [];
	params[ "fig_files" ] = [];
	params[ "bib_files" ] = [];
	params[ "sty_files" ] = [];
	params[ "cls_files" ] = [];
	params[ "texmf_include_dirs" ] = [];
	params[ "output_extension" ] = [ "pdf" ];
	params[ "graphics_paths" ] = [ "." ];
	params[ "sub_paths" ] = [];
	# TODO: make a bit more robust for differnt os's
	if os.path.exists( "~/Libarary/texmf" ):
		params[ "texmf_path" ] = "~/Libarary/texmf"
	else:
		params[ "texmf_path" ] = None;
	params[ "has_git" ] = functionExists( "git" );
	if params[ "has_git" ]:
		params[ "git" ] = which( "git" );
	else:
		params[ "git" ] = "";
		params[ "makediff" ] = False;
		print "Warning!";
		print "  git does not exist.";
		print "  Download from ";
		print "  The following makefile options will not be built:";
		print "    gitbkup";
		print "    .git";
		print "    .gitignore";
		print "    diff";

	params[ "has_latexpand" ] = functionExists( "latexpand" );
	if params[ "has_latexpand" ]:
		params[ "latexpand" ] = which( "latexpand" );
	else:
		params[ "latexpand" ] = "";
		params[ "makediff" ] = False;
		print "Warning!";
		print "  latexpand does not exist.";
		print "  Download from http://www.ctan.org/pkg/latexpand";
		print "  The following makefile options will not be built:";
		print "    diff";
		print "    onefile";

	params[ "has_bibsort" ] = functionExists( "bibsort" );
	if params[ "has_latexpand" ]:
		params[ "bibsort" ] = "bibsort";
	else:
		params[ "bibsort" ] = "";


	if not functionExists( "make" ):
		raise latexmake_makeDoesNotExist( "make is not in your path" );
	else:
		params[ "make" ] = which( "make" );

	params[ "has_latexdiff" ] = functionExists( "latexdiff" );
	if params[ "has_latexdiff" ]:
		params[ "latexdiff" ] = which( "latexdiff" );
	else:
		params[ "latexdiff" ] = "";
		params[ "makediff" ] = False;
		print "Warning!";
		print "  latexdiff does not exist.";
		print "  Download from http://latexdiff.berlios.de/";
		print "  The following makefile options will not be built:";
		print "    diff";

	params[ "has_mktemp" ] = functionExists( "mktemp" );
	if params[ "has_mktemp" ]:
		params[ "mktemp" ] = which( "mktemp" );
	else:
		params[ "mktemp" ] = "";
		params[ "makediff" ] = False;
		print "Warning!";
		print "  mktemp does not exist.";
		print "  The following makefile options will not be built:";
		print "    diff";


 	params[ "has_latex2rtf" ] = functionExists( "latex2rtf" );
 	if params[ "has_latex2rtf" ]:
		params[ "latex2rtf" ] = which( "latex2rtf" );
	else:
		params[ "latex2rtf" ] = "";
		print "Warning!";
		print "  latex2rtf does not exist.";
		print "  Download from http://latex2rtf.sourceforge.net/";
		print "  The following makefile options will not be built:";
		print "    rtf";
	params[ "latex2rtf_options" ] = "-M32";

	params[ "rm" ] = "rm";
	params[ "rm_options" ] = "-rf";
	params[ "echo" ] = "echo";
	params[ "find" ] = "find";
	params[ "unix_commands" ] = [ "rm", "echo", "find" ];
	if ( platform.system() == "Darwin" ):
		params[ "use_open" ] = True;
		params[ "open" ] = "open";
		params[ "unix_commands" ].append( "open" );
	else:
		params[ "use_open" ] = False;

	params[ "packages" ] = [];
	params[ "use_absolute_file_paths" ] = False;
	params[ "use_absolute_executable_paths" ] = True;
	params[ "verbose" ] = False;


	# set extensions
	params[ "fig_extensions" ] = [ ".pdf", ".png", ".jpg", ".jpeg" ];
	params[ "tex_aux_extensions" ] = [ ".aux", ".toc", ".lof", ".lot", \
	".lof", ".log", ".synctex.*" ];
	params[ "beamer_aux_extensions" ] =	[ ".nav", ".vrb", ".snm", ".out" ];
	params[ "bib_aux_extensions" ] = [ ".bbl", ".blg", ".bcf", ".run.xml", \
	"-blx.bib" ];
	params[ "figure_aux_extensions" ] = [ "-converted-to.pdf" ];
	params[ "idx_aux_extensions" ] = [ ".ilg", ".ind" ];
	params[ "latexmk_aux_extensions" ] = [ ".fdb_latexmk", ".fls" ];
	params[ "glossary_aux_extensions" ] = [ ".acn", ".acr", ".alg", ".glg", \
		".glo", ".gls", ".ist", ".lem", ".glsdefs" ];
	params[ "pkg_aux_extensions" ] = [ ".mw" ];

	params[ "clean_aux_extensions" ] = params[ "tex_aux_extensions" ] + \
	params[ "beamer_aux_extensions" ] + params[ "bib_aux_extensions" ] + \
	params[ "latexmk_aux_extensions" ] + params[ "idx_aux_extensions" ] + \
	params[ "glossary_aux_extensions" ] + params[ "pkg_aux_extensions" ];

	params[ "all_aux_extensions" ] = params[ "tex_aux_extensions" ] + \
	params[ "beamer_aux_extensions" ] + params[ "bib_aux_extensions" ] + \
	params[ "figure_aux_extensions" ] + params[ "latexmk_aux_extensions" ] + \
	params[ "idx_aux_extensions" ] + params[ "pkg_aux_extensions" ] + \
	params[ "glossary_aux_extensions" ];
	return params;
# fed latexmake_default_params()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def latexmake_finalize_params( params ):
	# set file paths to absolute or relative
	if params[ "use_absolute_file_paths" ]:
		#use absolute paths
		params[ "basepath" ] = os.path.abspath( params[ "basepath" ] );
		params[ "tex_files" ] = [ os.path.abspath( path ) \
			for path in params[ "tex_files" ] ];
		params[ "fig_files" ] = [ os.path.abspath( path ) \
			for path in params[ "fig_files" ] ];
		params[ "bib_files" ] = [ os.path.abspath( path ) \
			for path in params[ "bib_files" ] ];
		params[ "sty_files" ] = [ os.path.abspath( path ) \
			for path in params[ "sty_files" ] ];
		params[ "cls_files" ] = [ os.path.abspath( path ) \
			for path in params[ "cls_files" ] ];
		params[ "graphics_paths" ] = [ os.path.abspath( path ) \
			for path in params[ "graphics_paths" ] ];
		params[ "sub_paths" ] = [ os.path.abspath( path ) \
			for path in params[ "sub_paths" ] ];

	else:
		# use relative paths
		params[ "basepath" ] = os.path.relpath( params[ "basepath" ] );
		params[ "tex_files" ] = [ os.path.relpath( path ) \
			for path in params[ "tex_files" ] ];
		params[ "fig_files" ] = [ os.path.relpath( path ) \
			for path in params[ "fig_files" ] ];
		params[ "bib_files" ] = [ os.path.relpath( path ) \
			for path in params[ "bib_files" ] ];
		params[ "sty_files" ] = [ os.path.relpath( path ) \
			for path in params[ "sty_files" ] ];
		params[ "cls_files" ] = [ os.path.relpath( path ) \
			for path in params[ "cls_files" ] ];
		params[ "graphics_paths" ] = [ os.path.relpath( path ) \
			for path in params[ "graphics_paths" ] ];
		params[ "sub_paths" ] = [ os.path.relpath( path ) \
			for path in params[ "sub_paths" ] ];

	# set exicutible paths to absolute or relative
	if params[ "use_absolute_executable_paths" ]:
		# use absolute paths
		for command in params[ "unix_commands" ]:
			tmp = which( command );
			if tmp:
				params[ command ] = os.path.abspath( tmp );
			else:
				print "Warning!";
				print command + " is not found in your PATH";
	else:
		# use relative paths
		for command in params[ "unix_commands" ]:
			tmp = which( command );
			if not tmp:
				print "Warning!";
				print command + " is not found in your PATH";

	# TODO: remove duplicate aux_extensions

	return params;
# fed latexmake_finalize_params( params )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def write_makefile( fid, options ):
	# finalize the options
	options = latexmake_finalize_params( options );

	fid.write( "# Makefile\n" );

	# write some documentation about how created
	fid.write( latexmake_header() );
	fid.write( "\n\n" );

	# TeX commands
	fid.write( "# TeX commands (MODIFY AT YOUR OWN RISK)\n" );
	fid.write( "TEX=" + options[ "tex" ] + "\n" );
	fid.write( "LATEX=" + options[ "latex" ] + "\n" );
	fid.write( "PDFLATEX=" + options[ "pdflatex" ] + "\n" );
	fid.write( "LUATEX=" + options[ "luatex" ] + "\n" );
	fid.write( "LUALATEX=" + options[ "lualatex" ] + "\n" );
	fid.write( "XELATEX=" + options[ "xelatex" ] + "\n" );
	fid.write( "XETEX=" + options[ "xetex" ] + "\n" );
	fid.write( "BIBTEX=" + options[ "bibtex" ] + "\n" );
	fid.write( "BIBER=" + options[ "biber" ] + "\n" );
	fid.write( "DVIPS=" + options[ "dvips" ] + "\n" );
	fid.write( "PS2EPS=" + options[ "ps2eps" ] + "\n" );
	fid.write( "PSTOPDF=" + options[ "pstopdf" ] + "\n" );
	fid.write( "EPSTOPDF=" + options[ "epstopdf" ] + "\n" );
	fid.write( "MAKEGLOSSARIES=" + options[ "makeglossaries" ] + "\n" );
	fid.write( "MAKEINDEX=" + options[ "makeindex" ] + "\n" );
	fid.write( "LATEXDIFF=" + options[ "latexdiff" ] + "\n" );
	fid.write( "LATEXPAND=" + options[ "latexpand" ] + "\n" );
	fid.write( "LATEX2RTF=" + options[ "latex2rtf" ] + "\n" );
	fid.write( "BIBSORT=" + options[ "bibsort" ] + "\n" );
	fid.write( "# end TeX commands\n" );
	fid.write( "\n\n" );

	# write the tex engines
	fid.write( "# TeX commands and options\n" );
	fid.write( "TEX_ENGINE=${" + options[ "tex_engine" ] + "}\n" );
	fid.write( "BIB_ENGINE=${" + options[ "bib_engine" ] + "}\n" );
	fid.write( "IDX_ENGINE=${" + options[ "idx_engine" ] + "}\n" );
	fid.write( "GLS_ENGINE=${" + options[ "gls_engine" ] + "}\n" );
	fid.write( "\n" );

	# write the tex options
	fid.write( "# TeX commands\n" );
	fid.write( "TEX_OPTIONS=" + options[ "tex_options" ] + "\n" );
	fid.write( "LATEX2RTF_OPTIONS=" + options[ "latex2rtf_options" ] + "\n" );
	fid.write( "\n" );

	# write the other enigines of other uitilies
	fid.write( "# commands\n" )
	fid.write( "MAKE=" + options[ "make" ] + "\n" );
	fid.write( "RM=" + options[ "rm" ] + "\n" );
	fid.write( "RMO=" + options[ "rm_options" ] + "\n" );
	fid.write( "ECHO=" + options[ "echo" ] + "\n" );
	fid.write( "FIND=" + options[ "find" ] + "\n" );
	if options[ "has_git" ]:
		fid.write( "GIT=" + options[ "git" ] + "\n" );
	if options[ "use_open" ]:
		fid.write( "OPEN=" + options[ "open" ] + "\n" );
	if options[ "has_mktemp" ]:
		fid.write( "MKTEMP=" + options[ "mktemp" ] + "\n" );
	fid.write( "\n" );

	fid.write( "# Source Files\n" );
	fid.write( "SOURCE=" + options[ "basename" ] + "\n" );
	fid.write( "\n" );

	tmp = "TEX_FILES=";
	for f in options[ "tex_files" ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "BIB_FILES=";
	for f in options[ "bib_files" ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "FIG_FILES=";
	for f in options[ "fig_files" ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "STY_FILES=";
	for f in options[ "sty_files" ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "CLS_FILES=";
	for f in options[ "cls_files" ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );
	fid.write( "\n" );

	# paths

	fid.write( "# PATHS\n" );
	fid.write( "\n" );

	tmp = "SUB_PATHS="
	for f in options[ "sub_paths" ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	fid.write( "CLEANDIRS = $(SUB_PATHS:%=clean-%)\n" );
	fid.write( "\n" );

	# extensions

	fid.write( "\n" );
	fid.write( "# Sets of extensions\n" );
	tmp = "TEX_AUX_EXT=";
	for ext in options[ "tex_aux_extensions" ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "BIB_AUX_EXT=";
	for ext in options[ "bib_aux_extensions" ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "FIG_AUX_EXT=";
	for pth in options[ "graphics_paths" ]:
		for ext in options[ "figure_aux_extensions" ]:
			tmp += ( " " + os.path.join( pth, "*" + ext ) );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "IDX_AUX_EXT=";
	for ext in options[ "idx_aux_extensions" ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "BEAMER_AUX_EXT=";
	for ext in options[ "beamer_aux_extensions" ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "GLS_AUX_EXT=";
	for ext in options[ "glossary_aux_extensions" ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "PKG_AUX_EXT=";
	for ext in options[ "pkg_aux_extensions" ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n" );

	tmp = "ALL_AUX_EXT=";
	for ext in options[ "all_aux_extensions" ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n\n" );

	fid.write( "#" * 80 + "\n" );
	fid.write( "#" * 80 + "\n" );
	fid.write( "##\n" );
	fid.write( "##\tNo changes should have to be made after here\n" );
	fid.write( "##\n" );
	fid.write( "#" * 80 + "\n" );
	fid.write( "#" * 80 + "\n" );


	fid.write( "\n" );
	fid.write( "# all extensions\n" );
	fid.write( ".PHONY: all\n" );
	fid.write( "all: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}" );
	exts = options[ "output_extension" ];
	for ext in exts[ 1: ]:
		fid.write( " ${SOURCE}." + ext );
	fid.write( "\n" );
	if ( options[ "make_bib_in_default" ] or \
		options[ "make_index_in_default" ] or \
		options[ "make_glossary_in_default" ] ):
		fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );
		if options[ "make_bib_in_default" ]:
			fid.write( "\t${BIB_ENGINE} ${SOURCE}\n" );
		if options[ "make_index_in_default" ]:
			fid.write( "\t${IDX_ENGINE} ${SOURCE}\n" );
		if options[ "make_glossary_in_default" ]:
			fid.write( "\t${GLS_ENGINE} ${SOURCE}\n" );
	fid.write( "\t${MAKE} -e final\n" );
	if options[ "use_open" ]:
		fid.write( "\t${MAKE} -e view\n" );

	# write the code to make the main part of the makefile
	for ext in options[ "output_extension" ]:
		fid.write( "\n\n" );
		fid.write( "# the " + ext + " file\n" );
		fid.write( "${SOURCE}." + ext + ": ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n" );
		if options[ "make_bib_in_default" ] or options[ "make_index_in_default" ]:
			fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );
			if options[ "make_bib_in_default" ]:
				fid.write( "\t${BIB_ENGINE} ${SOURCE}\n" );
			if options[ "make_index_in_default" ]:
				fid.write( "\t${GLS_ENGINE} ${SOURCE}\n" );
		fid.write( "\t${MAKE} -e final\n" );

	# final is the last 2 latex compiles
	fid.write( "\n\n" );
	fid.write( "# final is the last 2 latex compiles\n" );
	fid.write( ".PHONY: final\n" );
	fid.write( "final: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n" );
	fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );
	fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );

	# update does not run the first latex
	fid.write( "\n\n" );
	fid.write( "# update is the last 2 latex compiles\n" );
	fid.write( ".PHONY: update\n" );
	fid.write( "update: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n" );
	if options[ "make_bib_in_default" ] or options[ "make_index_in_default" ]:
		if options[ "make_bib_in_default" ]:
			fid.write( "\t${BIB_ENGINE} ${SOURCE}\n" );
		if options[ "make_index_in_default" ]:
			fid.write( "\t${GLS_ENGINE} ${SOURCE}\n" );
	fid.write( "\t${MAKE} -e final\n" );

	# bibliography
	fid.write( "\n\n" );
	fid.write( "# make a bibliography\n" );
	fid.write( ".PHONY: bibliography\n" );
	fid.write( "bibliography: ${SOURCE}.aux ${TEX_FILES} ${BIB_FILES}\n" );
	fid.write( "\t${BIB_ENGINE} ${SOURCE}\n" );
	fid.write( "\t${MAKE} -e final\n" );

	# glossary
	fid.write( "\n\n" );
	fid.write( "# make a glossary\n" );
	fid.write( ".PHONY: glossary\n" );
	fid.write( "glossary: ${SOURCE}.aux ${TEX_FILES}\n" );
	fid.write( "\t${GLS_ENGINE} ${SOURCE}\n" );
	fid.write( "\t${MAKE} -e final\n" );

	# index
	fid.write( "\n\n" );
	fid.write( "# make a bibliography\n" );
	fid.write( ".PHONY: index\n" );
	fid.write( "index: ${SOURCE}.aux ${TEX_FILES}\n" );
	fid.write( "\t${IDX_ENGINE} ${SOURCE}\n" );
	fid.write( "\t{MAKE} -e final\n" );

	# some other builds that might be needed

	# open (on OS X)
	if options[ "use_open" ]:
		fid.write( "\n\n" );
		fid.write( "# Open the output file\n" );
		fid.write( ".PHONY: view\n" );
		fid.write( "view: ${SOURCE}.pdf\n" );
		fid.write( "\t${OPEN} ${SOURCE}.pdf\n" );

	# aux file / init
	fid.write( "\n\n" );
	fid.write( ".PHONY: init\n" );
	fid.write( "# the aux file, or an init\n" );
	fid.write( "${SOURCE}.aux init: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n" );
	fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );

	# clean
	fid.write( "\n\n" );
	fid.write( "# clean auxiliary files\n" );
	fid.write( ".PHONY: clean\n" );
	fid.write( "clean:\n" );
	fid.write( "\t${RM} ${RMO} ${ALL_AUX_EXT}\n" );

	# cleanall
	fid.write( "\n\n" );
	fid.write( "# clean all output files\n" );
	fid.write( ".PHONY: cleanall\n" );
	fid.write( "cleanall:\n" );
	tmp = "${RM} ${RMO} ${ALL_AUX_EXT}";
	for ext in [ "dvi", "ps", "eps", "pdf" ]:
		tmp += ( " ${SOURCE}." + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 1, False );

	# clean general
	fid.write( "\n\n" );
	fid.write( "# clean general auxiliary files\n" );
	fid.write( ".PHONY: cleangeneral\n" );
	fid.write( "cleangeneral:\n" );
	fid.write( "\t${RM} ${RMO} ${TEX_AUX_EXT}\n" );

	# clean beamer
	fid.write( "\n\n" );
	fid.write( "# clean beamer auxiliary files\n" );
	fid.write( ".PHONY: cleanbeamer\n" );
	fid.write( "cleanbeamer:\n" );
	fid.write( "\t${RM} ${RMO} ${BEAMER_AUX_EXT}\n" );

	# clean bib
	fid.write( "\n\n" );
	fid.write( "# clean bibliography auxiliary files\n" );
	fid.write( ".PHONY: cleanbib\n" );
	fid.write( "cleanbib:\n" );
	fid.write( "\t${RM} ${RMO} ${BIB_AUX_EXT}\n" );

	# clean figs
	fid.write( "\n\n" );
	fid.write( "# clean -converted-to.pdf files\n" );
	fid.write( ".PHONY: cleanfigs\n" );
	fid.write( "cleanfigs:\n" );
	tmp = "${RM} ${RMO}";
	for path in options[ "graphics_paths" ]:
		tmp += ( " " + os.path.join( path, "*-converted-to.pdf" ) );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 1, False );
	fid.write( "\n\n" );


	if options[ "has_latex2rtf" ]:
		fid.write( "\n\n" );
		fid.write( "# make rtf file\n" );
		fid.write( "${SOURCE}.rtf: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n" );
		fid.write( "\t${TEX2RTF} ${TEX2RTF_OPTIONS} ${SOURCE}.tex\n" );


	if options[ "has_git" ]:
		# git backup with message "bkup"
		fid.write( "\n\n" );
		fid.write( "# git backup\n" );
		fid.write( ".PHONY: gitbkup\n" );
		fid.write( "gitbkup: .git .gitignore .gitattributes\n" );
		fid.write( "\t${GIT} add -A\n" );
		fid.write( "\t${GIT} commit -m 'bkup'\n" );


		# git init ( so make gitbkup does not throw error if not a repository )
		fid.write( "\n\n" );
		fid.write( "# git init\n" );
		fid.write( ".git: .gitignore .gitattributes\n" );
		fid.write( "\t${GIT} init\n" );


		# .gitignore
		fid.write( "\n\n" );
		fid.write( "# .gitignore\n" );
		fid.write( ".gitignore:\n" );
		fid.write( "\t${ECHO} '# .gitignore' >> .gitignore\n" );
		header = latexmake_header().split( "\n" );
		for line in header:
			fid.write( "\t${ECHO} '" + line + "' >> .gitignore\n" );
		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# output files' >> .gitignore\n" );
		for ext in [ 'pdf', 'eps', 'ps', 'dvi' ]:
			fid.write( "\t${ECHO} ${SOURCE}." + ext + " >> .gitignore\n" );

		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# TeX auxiliary files' >> .gitignore\n" );
		for ext in options[ 'tex_aux_extensions' ]:
			fid.write( "\t${ECHO} '*" + ext + "' >> .gitignore\n" );

		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# beamer auxiliary files' >> .gitignore\n" );
		for ext in options[ 'beamer_aux_extensions' ]:
			fid.write( "\t${ECHO} '*" + ext + "' >> .gitignore\n" );

		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# bibliography auxiliary files' >> .gitignore\n" );
		for ext in options[ 'bib_aux_extensions' ]:
			fid.write( "\t${ECHO} '*" + ext + "' >> .gitignore\n" );

		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# latexmk auxiliary files' >> .gitignore\n" );
		for ext in options[ 'latexmk_aux_extensions' ]:
			fid.write( "\t${ECHO} '*" + ext + "' >> .gitignore\n" );

		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# package auxiliary files' >> .gitignore\n" );
		for ext in options[ 'pkg_aux_extensions' ]:
			fid.write( "\t${ECHO} '*" + ext + "' >> .gitignore\n" );

		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# glossary auxiliary files' >> .gitignore\n" );
		for ext in options[ 'glossary_aux_extensions' ]:
			fid.write( "\t${ECHO} '*" + ext + "' >> .gitignore\n" );

		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# package auxiliary files' >> .gitignore\n" );
		for ext in options[ 'pkg_aux_extensions' ]:
			fid.write( "\t${ECHO} '*" + ext + "' >> .gitignore\n" );

		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# converted figures' >> .gitignore\n" );
		for ext in options[ 'figure_aux_extensions' ]:
			fid.write( "\t${ECHO} '*" + ext + "' >> .gitignore\n" );
			for pth in options[ "graphics_paths" ]:
				fid.write( "\t${ECHO} '" + os.path.join( pth, \
					"*-converted-to.pdf" ) + "' >> .gitignore\n" );

		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# index auxiliary files' >> .gitignore\n" );
		for ext in options[ "idx_aux_extensions" ]:
			fid.write( "\t${ECHO} '*" + ext + "' >> .gitignore\n" );
		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# mac things' >> .gitignore\n" );
		fid.write( "\t${ECHO} '.DS_STORE' >> .gitignore\n" );

		fid.write( "\t${ECHO} '' >> .gitignore\n" );
		fid.write( "\t${ECHO} '# vi/vim swap file' >> .gitignore\n" );
		fid.write( "\t${ECHO} '*.swp' >> .gitignore\n" );

		# .gitattributes
		# see https://github.com/Danimoth/gitattributes
		fid.write( "\n\n" );
		fid.write( "# .gitattributes\n" );
		fid.write( ".gitattributes:\n" );
		fid.write( "\t${ECHO} '# .gitattributes' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '' >> .gitattributes\n" );
		header = latexmake_header().split( "\n" );
		for line in header:
			fid.write( "\t${ECHO} '" + line + "' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '# Auto detect text files and perform LF normalization' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '* text=auto' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '#' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '# The above will handle all files NOT found below' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '#' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.tex\tdiff=tex' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.sty\tdiff=tex' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.cls\tdiff=tex' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.pdf\tdiff=astextplain' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.PDF\tdiff=astextplain' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.eps\tdiff=astextplain' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.EPS\tdiff=astextplain' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.png\tbinary' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.PNG\tbinary' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.jpg\tbinary' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.JPG\tbinary' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.jpeg\tbinary' >> .gitattributes\n" );
		fid.write( "\t${ECHO} '*.JPEG\tbinary' >> .gitattributes\n" );




	if options[ "makediff" ]:
		# right now will use the master branch of .
		# latex diff
		fid.write( "\n\n" );
		fid.write( "# make difference\n" );
		fid.write( ".PHONY: diff\n" );
		fid.write( "diff: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n" );
		# make a temporary directory
		fid.write( "\t$(eval TMP := $(shell ${MKTEMP} -d -t latexmake))\n" );
		fid.write( "\t@echo 'created a temp directory in ' $(TMP)\n"); # I have no idea why @echo works. I stole it from http://stackoverflow.com/questions/1909188/define-make-variable-at-rule-execution-time
		# # make some folders
		# fid.write( "\tmkdir ${TMP}/new\n" );
		# fid.write( "\tmkdir ${TMP}/old\n" );
		fid.write( "\tgit clone . ${TMP}\n" );

		# make the original file
		fid.write( "\t${LATEXPAND} ${TMP}/${SOURCE}.tex > ${TMP}/orig.tex\n" );
		fid.write( "\t${LATEXDIFF} ${TMP}/orig.tex ${SOURCE}_one_file.tex > ${SOURCE}_diff.tex\n" );

		# compile the difference file
		if ( options[ "make_bib_in_default" ] or \
			options[ "make_index_in_default" ] or \
			options[ "make_glossary_in_default" ] ):
			fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}_diff.tex\n" );
			if options[ "make_bib_in_default" ]:
				fid.write( "\t${BIB_ENGINE} ${SOURCE}_diff\n" );
			if options[ "make_index_in_default" ]:
				fid.write( "\t${IDX_ENGINE} ${SOURCE}_diff\n" );
			if options[ "make_glossary_in_default" ]:
				fid.write( "\t${GLS_ENGINE} ${SOURCE}_diff\n" );
			fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}_diff.tex\n" );
			fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}_diff.tex\n" );
			if options[ "use_open" ]:
				fid.write( "\t${OPEN} ${SOURCE}_diff.pdf\n" );



		# remove the tempory directory
		fid.write( "\t${RM} ${RMO} ${TMP}\n" );

	# latex diff
	fid.write( "\n\n" );
	fid.write( "# clean difference stuff\n" );
	fid.write( ".PHONY: cleandiff\n" );
	fid.write( "cleandiff:\n" );
	fid.write( "\t${RM} ${RMO} ${SOURCE}_diff.*" );

	if options[ "has_latexpand" ]:
		# expand source
		fid.write( "\n\n" );
		fid.write( "# Expand Source \n" );
		fid.write( ".PHONY: onefile\n" );
		fid.write( "onefile: \n" );
		fid.write( "\t${LATEXPAND} ${SOURCE}.tex > ${SOURCE}_one_file.tex\n" );

		fid.write( "\n\n" );
		fid.write( "# Expand Source \n" );
		fid.write( "${SOURCE}_one_file.tex: ${TEX_FILES}\n" );
		fid.write( "\t${LATEXPAND} ${SOURCE}.tex > ${SOURCE}_one_file.tex\n" );


	# tools
	fid.write( "\n\n" );
	fid.write( "# tools\n" );
	fid.write( ".PHONY: rmlog\n" );
	fid.write( "rmlog:\n" );
	fid.write( "\t${FIND} . -name '*.log' -exec ${RM} ${RMO} {} \;\n" );
	return;
# fed write_makefile( fid )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def latexmake_parse_inputs():
	args = sys.argv;
	try:
		if not args:
			raise latexmake_noInput( "no inputs from latexmake_parse_inputs()\n" );
		# set the default parameters
		output = latexmake_default_params();

		# get the file name (always last argument)
		tmp = args[ -1 ];

		# make sure the file exists
		if not os.path.isfile( tmp ):
			# we may have left the extension off
			tmp += ".tex";
			if not os.path.isfile( tmp ):
				raise latexmake_nonexistantFile( tmp );


		# get the absolute path to the source file
		( pth, tmp ) = os.path.split( os.path.abspath( tmp ) );
		output[ "path" ] = pth;

		idx = tmp.find( ".tex" );

		output[ "tex_files" ].append( os.path.abspath( tmp ) );

		if idx < 0:
			raise latexmake_invalidBasename( tmp );
		else:
			tmp = tmp[ :idx ]
		output[ "basename" ] = tmp;

		for arg in args[1:-1]:
			if arg.find( "--tex=" ) == 0:
				pass;
			elif arg.find( "--bib=" ) == 0:
				pass;
			#else:
			#	raise latexmake_invalidArgument( arg );


	except latexmake_noInput, e:
		raise latexmake_noInput( e.args );
	except latexmake_invalidBasename, e:
		raise latexmake_invalidBasename( e.args );
	except latexmake_nonexistantFile, e:
		raise latexmake_nonexistantFile( e.args );
	except latexmake_invalidArgument, e:
		raise latexmake_invalidArgument( e.args );
	#except Exception, e;
	#	raise Exception( e.args );
	else:
		return output;
# fed latexmake_parse_inputs():
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def main():

	# parse the parameters
	params = latexmake_parse_inputs();

	params = parseLatexFile( params[ "basename" ] + ".tex", params );

	# open the Makefile
	fid = open( "Makefile", "w" );

	# write the Makefile
	write_makefile( fid, params );

	# close the makefile
	fid.close();

	return;
#fed main()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
if __name__ == "__main__":
	main();
# __name__ == "__main__"
#-------------------------------------------------------------------------------