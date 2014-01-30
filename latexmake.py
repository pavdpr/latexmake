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
# TODO:
#	- Fix ability to read in multiline package commands
#		+ Strip all newlines?
#	- Add in latexdiff support
#		+ use gitlatexdiff https://github.com/daverted/gitlatexdiff as an example
#	- Add in git support
#
# COPYRIGHT:
#	Copyright 2014 Paul Romanczyk
#
# REFERENCES:
#	[1] http://users.phys.psu.edu/~collins/software/latexmk-jcc/ [2014-01-08]
#	[*] http://tex.stackexchange.com/questions/7770/file-extensions-of-latex-related-files
#	
#

import os;
import re
import sys;
import datetime;


latexmake_version_major = 0;
latexmake_version_minor = 0;
latexmake_version_revision = 1;


#================================================================================
#
#		Exception Classes
#
#================================================================================


#-------------------------------------------------------------------------------
class latexmake_invalidInput(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_invalidInput(RuntimeError)
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_noInput(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_noInput(RuntimeError)
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_invalidBasename(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_invalidBasename(RuntimeError)
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_nonexistantFile(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_invalidBasename(RuntimeError)
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_invalidArgument(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_invalidArgument(RuntimeError)
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class latexmake_invalidBracketOrder(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_invalidArgument(RuntimeError)
#-------------------------------------------------------------------------------


#================================================================================
#
#		Executable testing code
#
#================================================================================


#-------------------------------------------------------------------------------
def is_exe(fpath):
	# used to see if fpath is an executable
	# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
	return os.path.isfile(fpath) and os.access(fpath, os.X_OK);
# fed is_exe( fpath )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def functionExists(program):

	fpath, fname = os.path.split(program);
	if fpath:
		return is_exe(program);
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			path = path.strip('"');
			exe_file = os.path.join(path, program );
			if is_exe( exe_file ):
				return True;

		return False;
# fed functionExists( program )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def which(program):
	# a unix-like which
	# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python

	fpath, fname = os.path.split(program);
	if fpath:
		if is_exe(program):
			return program;
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			path = path.strip('"');
			exe_file = os.path.join(path, program);
			if is_exe(exe_file):
				return exe_file;

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
	output = 'latexmake [options] basefilename\n';
	output += '\t--tex=/path/to/tex compiler\n';
	output += '\t--bib=/path/to/bib compiler\n';
	#output += '\t--nooverwrite\t\t\tWill not overwrite a Makefile\n';
	return output
# fed latexmake_usage()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def latexmake_copyright():
	output = 'latexmake\n';
	output += '\n\tCopyright 2014 Paul Romanczyk\n';
	return output
# fed latexmake_copyright()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def latexmake_version():
	output = \
	str( latexmake_version_major ) + '.' + \
	str( latexmake_version_minor ) + '.' + \
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

	tabs = '';
	for i in range( 0, numTabs ):
		tabs += "\t";

	if not extra:
		for l in lines[:-1]:
			fid.write( tabs + l + " \\\n" );
		fid.write( tabs + lines[-1] + "\n" );
	else:
		fid.write( tabs + lines[0] + " \\\n" );
		tabs += "\t";
		for l in lines[1:-1]:
			fid.write( tabs + l + " \\\n" );
		fid.write( tabs + lines[-1] + "\n" );
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
		return (left, right);
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
def parseDataInSquiglyBraces( line ):
	output = [];
	lstack = [];

	lidx = findUnescaped( line, "{" );
	ridx = findUnescaped( line, "}" );

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
					message += "\tunbalanced {}";
					raise latexmake_invalidBracketOrder( message );
			else:
				lstack.append( lidx );
				tmp = findUnescaped( line[ lidx+1:], "{" );
				if tmp < 0:
					lidx = -1;
				else:
					lidx += tmp + 1;
		elif lidx < ridx and lidx > 0:
			lstack.append( lidx );
			tmp = findUnescaped( line[ lidx+1:], "{" );
			if tmp < 0:
				lidx = -1;
			else:
				lidx += tmp + 1;
		elif ridx >= 0:
			if ( len( lstack  ) == 0 ):
				message = "In string: '" + line + "':\n";
				message += "\tunbalanced {}";
				raise latexmake_invalidBracketOrder( message );
			elif lstack[-1] >= ridx:
				message = "In string: '" + line + "':\n";
				message += "\t'}' appears before '{'";
				raise latexmake_invalidBracketOrder( message );

			output.append( line[ lstack.pop() + 1:ridx ] );
			tmp = findUnescaped( line[ ridx+1:], "}" );
			if tmp < 0:
				ridx = -1;
			else:
				ridx += tmp + 1;
		else:
			if findUnescaped( line[ ridx+1:], "}" ) < 0:
				run = False;
			else:
				message = "In string: '" + line + "':\n";
				message += "\tunbalanced {}";
				raise latexmake_invalidBracketOrder( message );

	return output;
# fed parseDataInSquiglyBraces( line )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def parseDataInSquareBraces( line ):
	output = [];
	lstack = [];

	lidx = findUnescaped( line, "[" );
	ridx = findUnescaped( line, "]" );

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
					message += "\tunbalanced []";
					raise latexmake_invalidBracketOrder( message );
			else:
				lstack.append( lidx );
				tmp = findUnescaped( line[ lidx+1:], "[" );
				if tmp < 0:
					lidx = -1;
				else:
					lidx += tmp + 1;
		elif lidx < ridx and lidx > 0:
			lstack.append( lidx );
			tmp = findUnescaped( line[ lidx+1:], "[" );
			if tmp < 0:
				lidx = -1;
			else:
				lidx += tmp + 1;
		elif ridx >= 0:
			if ( len( lstack  ) == 0 ):
				message = "In string: '" + line + "':\n";
				message += "\tunbalanced []";
				raise latexmake_invalidBracketOrder( message );
			elif lstack[-1] >= ridx:
				message = "In string: '" + line + "':\n";
				message += "\t']' appears before '['";
				raise latexmake_invalidBracketOrder( message );

			output.append( line[ lstack.pop() + 1:ridx ] );
			tmp = findUnescaped( line[ ridx+1:], "]" );
			if tmp < 0:
				ridx = -1;
			else:
				ridx += tmp + 1;
		else:
			if findUnescaped( line[ ridx+1:], "]" ) < 0:
				run = False;
			else:
				message = "In string: '" + line + "':\n";
				message += "\tunbalanced []";
				raise latexmake_invalidBracketOrder( message );

	return output;
# fed parseDataInSquareBraces( line )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def parseDataInParentheses( line ):
	output = [];
	lstack = [];

	lidx = findUnescaped( line, "(" );
	ridx = findUnescaped( line, ")" );

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
					message += "\tunbalanced ()";
					raise latexmake_invalidBracketOrder( message );
			else:
				lstack.append( lidx );
				tmp = findUnescaped( line[ lidx+1:], "(" );
				if tmp < 0:
					lidx = -1;
				else:
					lidx += tmp + 1;
		elif lidx < ridx and lidx > 0:
			lstack.append( lidx );
			tmp = findUnescaped( line[ lidx+1:], "(" );
			if tmp < 0:
				lidx = -1;
			else:
				lidx += tmp + 1;
		elif ridx >= 0:
			if ( len( lstack  ) == 0 ):
				message = "In string: '" + line + "':\n";
				message += "\tunbalanced ()";
				raise latexmake_invalidBracketOrder( message );
			elif lstack[-1] >= ridx:
				message = "In string: '" + line + "':\n";
				message += "\t')' appears before '('";
				raise latexmake_invalidBracketOrder( message );

			output.append( line[ lstack.pop() + 1:ridx ] );
			tmp = findUnescaped( line[ ridx+1:], ")" );
			if tmp < 0:
				ridx = -1;
			else:
				ridx += tmp + 1;
		else:
			if findUnescaped( line[ ridx+1:], ")" ) < 0:
				run = False;
			else:
				message = "In string: '" + line + "':\n";
				message += "\tunbalanced ()";
				raise latexmake_invalidBracketOrder( message );

	return output;
# fed parseDataInParenthesies( line )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def parseDataInAngleBraces( line ):
	lstack = [];

	lidx = findUnescaped( line, "<" );
	ridx = findUnescaped( line, ">" );

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
					message += "\tunbalanced <>";
					raise latexmake_invalidBracketOrder( message );
			else:
				lstack.append( lidx );
				tmp = findUnescaped( line[ lidx+1:], "<" );
				if tmp < 0:
					lidx = -1;
				else:
					lidx += tmp + 1;
		elif lidx < ridx and lidx > 0:
			lstack.append( lidx );
			tmp = findUnescaped( line[ lidx+1:], "<" );
			if tmp < 0:
				lidx = -1;
			else:
				lidx += tmp + 1;
		elif ridx >= 0:
			if ( len( lstack  ) == 0 ):
				message = "In string: '" + line + "':\n";
				message += "\tunbalanced <>";
				raise latexmake_invalidBracketOrder( message );
			elif lstack[-1] >= ridx:
				message = "In string: '" + line + "':\n";
				message += "\t'>' appears before '<'";
				raise latexmake_invalidBracketOrder( message );

			output.append( line[ lstack.pop() + 1:ridx ] );
			tmp = findUnescaped( line[ ridx+1:], ">" );
			if tmp < 0:
				ridx = -1;
			else:
				ridx += tmp + 1;
		else:
			if findUnescaped( line[ ridx+1:], ">" ) < 0:
				run = False;
			else:
				message = "In string: '" + line + "':\n";
				message += "\tunbalanced <>";
				raise latexmake_invalidBracketOrder( message );

	return output;
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
def removeTeXcomments( texFile, thisFileName ):
	texFileList = texFile.splitlines();
	output = "";
	for line in texFileList:

		# remove empty lines as well
		if len( line ) > 0:
			loc = line.find( '%' );
			if loc < 0:
				output += ( line + "\n" );
			elif loc > 0:
				run = True;
				tmp = "";
				while run:
					if len( line ) == 0:
						run = False;
					elif loc < 0:
						tmp += line;
						run = False;
					elif loc > 0:
						if line[loc-1] != "\\":
							# We have a real comment and not an escaped one
							tmp += line[:loc];
							run = False;
						else:
							# we have an escaped comment, this is valid
							tmp += line[:loc+1];
							line = line[loc+1:];
							loc = line.find( "%" )
							# run = True;
					else:
						# loc is 0
						run = False;
				if len( tmp ) > 0:
					output += ( tmp + "\n" );	
			else:
				# remove lines that are all comment
				# do nothing here
				pass;
	return output
# fed removeTeXcomments( texFile )
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
							params[ "bib_engine" ] = which( backend );
						else:
							warning( "The bibliography backend \"" + backend + \
								"\" cannot be found" );

				elif package == "epstopdf":
					if params[ 'tex_engine' ] == "pdflatex":
						params[ "fig_extensions" ] += ".eps";

				elif package == "makeidx":
					params[ "make_index_in_default" ] = True;

	# update the packages list in params				
	params[ 'packages' ] += packages;
	return params;
# fed findPackages( texFile, params )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findGraphicsPaths( texFile, params, thisFileName ):
	locs = re.findall( r'\\graphicspath\{(.*)\}', texFile );
	graphicsPaths = [];
	for line in locs:
		for part in purifyListOfStrings( parseDataInSquiglyBraces( line ), \
			r"[\{\}]" ):
			if os.path.isdir( part ) and os.path.exists( part ):
				# we are a valid path
				params[ "graphics_paths" ].append( os.path.abspath( part ) );
			else:
				#TODO?: raise exception
				warning( "In \"" + thisFileName + "\": \"" + part + \
					"\" is not a valid graphicspath" );
	return params;
# fed findGraphicsPaths( texFile, params )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findGraphicsExtensions( texFile, params, thisFileName ):
	locs = re.findall( r'\\DeclareGraphicsExtensions\{(.*)\}', texFile );
	if not locs:
		return params;
	for item in locs:
		if parseDataInSquiglyBraces( item ):
			# residual squiglies
			item = parseDataInSquiglyBraces( item );
			params[ "fig_extensions"] = parseCommaSeparatedData( item );
			#TODO: check to see if I can have a .jpg if the g.e. is just .eps
	return params;
# fed findGraphicsExtensions( texFile, params )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def findFigures( texFile, params, thisFileName ):
	# TODO: also get pgf figures
	m = re.findall( r'\\includegraphics(\[.*\])?(\{.*\})', texFile );
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
	key = r"\\(include|input)(\[.*\])?(\{.*\})";
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
					# parse the sub tex file
					params = parse_latex_file( f, params );

		
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
		if styname in files:
			f = os.path.abspath( styname );
		elif ( styname + ".sty" ) in files:
			f = os.path.abspath( styname + ".sty" );

		if f:
			params[ "sty_files" ].append( f );
			
			#parse the included local style file
			params = parse_latex_file( f, params )

	return params;
# fed findLocalStyFiles( styfilename, params, thisFileName )
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
def parse_latex_file( filename, params ):
	fid = open( filename, 'r' );
	if fid < 0:
		raise latexmake_nonexistantFile( filename );

	texFile = fid.read();
	fid.close();

	# TODO: look for latexmk directives here

	# remove the comments
	texFile = removeTeXcomments( texFile, filename );

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

	return params;

# fed parse_latex_file( file )
#-------------------------------------------------------------------------------


#================================================================================
#
#		Meat and Potatoes
#
#================================================================================


#-------------------------------------------------------------------------------
def latexmake_default_params():
	params = {};
	params[ 'tex_engine' ] = which( 'pdflatex' );
	params[ 'tex_options' ] = '--file-line-error';
	params[ 'bib_engine' ] = which( 'bibtex' );
	params[ 'idx_engine' ] = which( 'makeindex' );
	params[ 'make_bib_in_default' ] = False;
	params[ 'make_index_in_default' ] = False;
	params[ 'basename' ] = '';
	params[ 'basepath' ] = os.path.abspath( "." );
	params[ 'tex_files' ] = [];
	params[ 'fig_files' ] = [];
	params[ 'bib_files' ] = [];
	params[ 'sty_files' ] = [];
	params[ 'cls_files' ] = [];
	params[ 'texmf_include_dirs' ] = [];
	params[ 'output_extension' ] = [ 'pdf' ];
	params[ 'graphics_paths' ] = [ "." ];
	# TODO: make a bit more robust for differnt os's
	if os.path.exists( "~/Libarary/texmf" ):
		params[ 'texmf_path' ] = "~/Libarary/texmf"
	else:
		params[ 'texmf_path' ] = None;
	params[ 'has_git' ] = functionExists( 'git' );
	if params[ 'has_git' ]:
		params[ 'git' ] = which( "git" );
	else:
		params[ 'git' ] = "";

 	params[ 'has_latex2rft' ] = functionExists( 'latex2rtf' );
 	if params[ 'has_latex2rft' ]:
		params[ 'latex2rtf' ] = which( "latex2rtf" );
	else:
		params[ 'latex2rtf' ] = "";
	params[ 'latex2rtf_options' ] = '-M32';

	params[ 'rm' ] = which( 'rm' );
	params[ 'rm_options' ] = '-rf';
	params[ 'packages' ] = [];
	params[ 'use_absolute_file_paths' ] = False;
	params[ 'use_absolute_executable_paths' ] = True;
	params[ "verbose" ] = False;

	# set extensions
	params[ 'fig_extensions' ] = [ ".pdf", ".png", ".jpg", ".jpeg" ];
	params[ 'tex_aux_extensions' ] = [ '.aux', '.toc', '.lof', '.lot', \
	'.lof', '.log', '.synctex.gz' ];
	params[ 'beamer_aux_extensions' ] =	[ '.nav', '.vrb', '.snm', '.out' ];
	params[ 'bib_aux_extensions' ] = [ '.bbl', '.blg', '.bcf', '.run.xml', \
	'-blx.bib' ];
	params[ 'figure_aux_extensions' ] = [ '-converted-to.pdf' ];
	params[ 'idx_aux_extensions' ] = [ '.ilg', '.ind' ];
	params[ 'latexmk_aux_extensions' ] = [ '.fdb_latexmk', '.fls' ];

	params[ 'clean_aux_extensions' ] = params[ 'tex_aux_extensions' ] + \
	params[ 'beamer_aux_extensions' ] + params[ 'bib_aux_extensions' ] + \
	params[ 'latexmk_aux_extensions' ] + params[ 'idx_aux_extensions' ];

	params[ 'all_aux_extensions' ] = params[ 'tex_aux_extensions' ] + \
	params[ 'beamer_aux_extensions' ] + params[ 'bib_aux_extensions' ] + \
	params[ 'figure_aux_extensions' ] + params[ 'latexmk_aux_extensions' ] + \
	params[ 'idx_aux_extensions' ];
	return params;
# fed latexmake_default_params()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def latexmake_finalize_params( params ):
	# set file paths to absolute or relative
	if params[ 'use_absolute_file_paths' ]:
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

	# set exicutible paths to absolute or relative
	if params[ "use_absolute_executable_paths" ]:
		# use absolute paths
		params[ 'rm' ] = os.path.abspath( params[ 'rm' ] );
		pass;
	else:
		# use relative paths
		pass;

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

	# write the tex engines
	fid.write( "# TeX commands\n" );
	fid.write( "TEX_ENGINE=" + options[ "tex_engine" ] + '\n' );
	fid.write( "TEX_OPTIONS=" + options[ "tex_options" ] + '\n' );
	fid.write( "BIB_ENGINE=" + options[ "bib_engine" ] + '\n' );
	fid.write( "IDX_ENGINE=" + options[ "idx_engine" ] + '\n' );
	fid.write( "\n" );
	# write the other enigines of other uitilies
	fid.write( "# commands\n" )
	fid.write( "RM=" + options[ "rm" ] + "\n" );
	fid.write( "RMO=" + options[ "rm_options" ] + "\n" );
	if options[ "has_git" ]:
		fid.write( "GIT=" + options[ "git" ] + "\n" );
	fid.write( "\n" );
	fid.write( "# Source Files\n" );
	fid.write( "SOURCE=" + options[ "basename" ] + '\n' );
	
	tmp = "TEX_FILES=";
	for f in options[ 'tex_files' ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );

	tmp = "BIB_FILES=";
	for f in options[ 'bib_files' ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );

	tmp = "FIG_FILES=";
	for f in options[ 'fig_files' ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );

	tmp = "STY_FILES=";
	for f in options[ 'sty_files' ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );

	tmp = "CLS_FILES=";
	for f in options[ 'cls_files' ]:
		tmp += ( " " + f );
	tmp += ( "\n" );
	writeLongLines( fid, tmp, 80, 8, 0, False );

	fid.write( "\n" );
	fid.write( "# Sets of extensions\n" );
	tmp = "TEX_AUX_EXT=";
	for ext in options[ 'tex_aux_extensions' ]:
		tmp += ( " *" + ext );
	tmp += "\n";

	writeLongLines( fid, tmp, 80, 8, 0, False );
	tmp = "BIB_AUX_EXT=";
	for ext in options[ 'bib_aux_extensions' ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );

	tmp = "FIG_AUX_EXT=";
	for ext in options[ 'figure_aux_extensions' ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );

	tmp = "IDX_AUX_EXT=";
	for ext in options[ 'idx_aux_extensions' ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );

	tmp = "BEAMER_AUX_EXT=";
	for ext in options[ 'beamer_aux_extensions' ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );

	tmp = "ALL_AUX_EXT=";
	for ext in options[ 'all_aux_extensions' ]:
		tmp += ( " *" + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 0, False );
	fid.write( "\n\n" );
	
	fid.write( "########################################" + \
		"########################################\n" );
	fid.write( "########################################" + \
		"########################################\n" );
	fid.write( "##\n" );
	fid.write( "##\tNo changes should have to be made after here\n" );
	fid.write( "##\n" );
	fid.write( "########################################" + \
		"########################################\n" );
	fid.write( "########################################" + \
		"########################################\n" );


	fid.write( "\n" );
	fid.write( "# all extensions\n" );
	fid.write( ".PHONY: all\n" );
	fid.write( "all: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}" );
	exts = options[ 'output_extension' ];
	for ext in exts[ 1: ]:
		fid.write( " ${SOURCE}." + ext );
	fid.write( "\n" );
	if options[ "make_bib_in_default" ] or options[ "make_index_in_default" ]:
		fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );
		if options[ "make_bib_in_default" ]:
			fid.write( "\t${BIB_ENGINE} ${SOURCE}\n" );
		if options[ "make_index_in_default" ]:
			fid.write( "\t${IDX_ENGINE} ${SOURCE}\n" );
			# TODO: add index engine
	fid.write( "\tmake -e final\n" );

	# write the code to make the main part of the makefile
	for ext in options[ 'output_extension' ]:
		fid.write( "\n\n" );
		fid.write( "# the " + ext + " file\n" );
		fid.write( "${SOURCE}." + ext + ": ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n" );
		if options[ "make_bib_in_default" ] or options[ "make_index_in_default" ]:
			fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );
			if options[ "make_bib_in_default" ]:
				fid.write( "\t${BIB_ENGINE} ${SOURCE}\n" );
			if options[ "make_index_in_default" ]:
				pass;
		fid.write( "\tmake -e final\n" );

	# final is the last 2 latex compiles
	fid.write( "\n\n" );
	fid.write( "# final is the last 2 latex compiles\n" );
	fid.write( '.PHONY: final\n');
	fid.write( 'final: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n');
	fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );
	fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );

	# bibliography
	fid.write( "\n\n" );
	fid.write( "# make a bibliography\n" );
	fid.write( '.PHONY: bibliography\n');
	fid.write( 'bibliography: ${SOURCE}.aux ${TEX_FILES} ${BIB_FILES}\n');
	fid.write( "\t${BIB_ENGINE} ${SOURCE}\n" );
	fid.write( "\tmake -e final\n" );

	# index
	fid.write( "\n\n" );
	fid.write( "# make a bibliography\n" );
	fid.write( '.PHONY: index\n');
	fid.write( 'index: ${SOURCE}.aux ${TEX_FILES}\n');
	fid.write( "\t${IDX_ENGINE} ${SOURCE}\n" );
	fid.write( "\tmake -e final\n" );

	# some other builds that might be needed


	# aux file / init
	fid.write( "\n\n" );
	fid.write( ".PHONY: init\n" );
	fid.write( "# the aux file, or an init\n" );
	fid.write( "${SOURCE}.aux init: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n" );
	fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );

	# clean
	fid.write( "\n\n" );
	fid.write( "# clean auxiliary files\n" );
	fid.write( '.PHONY: clean\n');
	fid.write( 'clean:\n');
	fid.write( "\t${RM} ${RMO} ${ALL_AUX_EXT}\n" );

	# cleanall
	fid.write( "\n\n" );
	fid.write( "# clean all output files\n" );
	fid.write( '.PHONY: cleanall\n');
	fid.write( 'cleanall:\n');
	tmp = "${RM} ${RMO} ${ALL_AUX_EXT}";
	for ext in [ "dvi", "ps", "eps", "pdf" ]:
		tmp += ( " ${SOURCE}." + ext );
	tmp += "\n";
	writeLongLines( fid, tmp, 80, 8, 1, False );

	# clean general
	fid.write( "\n\n" );
	fid.write( "# clean general auxiliary files\n" );
	fid.write( '.PHONY: cleangeneral\n');
	fid.write( 'cleangeneral:\n');
	fid.write( "\t${RM} ${RMO} ${TEX_AUX_EXT}\n" );

	# clean beamer
	fid.write( "\n\n" );
	fid.write( "# clean beamer auxiliary files\n" );
	fid.write( '.PHONY: cleanbeamer\n');
	fid.write( 'cleanbeamer:\n');
	fid.write( "\t${RM} ${RMO} ${BEAMER_AUX_EXT}\n" );

	# clean bib
	fid.write( "\n\n" );
	fid.write( "# clean bibliography auxiliary files\n" );
	fid.write( '.PHONY: cleanbib\n');
	fid.write( 'cleanbib:\n');
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


	if options[ "has_latex2rft" ]:
		fid.write( "\n\n" );
		fid.write( "# make rtf file\n" );
		fid.write( "${SOURCE}.rtf: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n" );
		fid.write( "\t${TEX2RTF} ${TEX2RTF_OPTIONS} ${SOURCE}.tex\n" );


	if options[ "has_git" ]:
		# git backup with message 'bkup'
		fid.write( "\n\n" );
		fid.write( "# git backup\n" );
		fid.write( ".PHONY: gitbkup\n" );
		fid.write( "gitbkup: .git .gitignore\n" );
		fid.write( "\t${GIT} add -A\n" );
		fid.write( "\t${GIT} commit -m 'bkup'\n" );
		

		# git init ( so make gitbkup does not throw error if not a repository )
		fid.write( "\n\n" );
		fid.write( "# git init\n" );
		fid.write( ".git:\n" );
		fid.write( "\t${GIT} init\n" );
		

		# .gitignore
		fid.write( "\n\n" );
		fid.write( "# .gitignore\n" );
		fid.write( ".gitignore:\n" );
		fid.write( "\techo '# .gitignore' >> .gitignore\n" );
		header = latexmake_header().split( "\n" );
		for line in header:
			fid.write( "\techo '" + line + "' >> .gitignore\n" );
		fid.write( "\techo '' >> .gitignore\n" );
		fid.write( "\techo '# output files' >> .gitignore\n" );
		for ext in [ 'pdf', 'eps', 'ps', 'dvi' ]:
			fid.write( "\techo ${SOURCE}." + ext + " >> .gitignore\n" );
		fid.write( "\techo '' >> .gitignore\n" );
		fid.write( "\techo '# TeX auxiliary files' >> .gitignore\n" );
		for ext in options[ 'tex_aux_extensions' ]:
			fid.write( "\techo '*" + ext + "' >> .gitignore\n" );
		fid.write( "\techo '' >> .gitignore\n" );
		fid.write( "\techo '# beamer auxiliary files' >> .gitignore\n" );
		for ext in options[ 'beamer_aux_extensions' ]:
			fid.write( "\techo '*" + ext + "' >> .gitignore\n" );
		fid.write( "\techo '' >> .gitignore\n" );
		fid.write( "\techo '# bibliography auxiliary files' >> .gitignore\n" );
		for ext in options[ 'bib_aux_extensions' ]:
			fid.write( "\techo '*" + ext + "' >> .gitignore\n" );
		fid.write( "\techo '' >> .gitignore\n" );
		fid.write( "\techo '# latexmk auxiliary files' >> .gitignore\n" );
		for ext in options[ 'latexmk_aux_extensions' ]:
			fid.write( "\techo '*" + ext + "' >> .gitignore\n" );
		fid.write( "\techo '# converted figures' >> .gitignore\n" );
		for ext in options[ 'figure_aux_extensions' ]:
			fid.write( "\techo '*" + ext + "' >> .gitignore\n" );
			for pth in options[ "graphics_paths" ]:
				fid.write( "\techo '" + os.path.join( pth, \
					"*-converted-to.pdf" ) + "' >> .gitignore\n" );
		fid.write( "\techo '# index auxiliary files' >> .gitignore\n" );
		for ext in options[ "idx_aux_extensions" ]:
			fid.write( "\techo '*" + ext + "' >> .gitignore\n" );
		fid.write( "\techo '' >> .gitignore\n" );
		fid.write( "\techo '# mac things' >> .gitignore\n" );
		fid.write( "\techo '.DS_STORE' >> .gitignore\n" );



	return;
# fed write_makefile( fid )
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def latexmake_parse_inputs():
	args = sys.argv;
	try:
		if not args:
			raise latexmake_noInput( "no inputs from latexmake_parse_inputs()\n");
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
		output[ 'basename' ] = tmp;

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
	
	params = parse_latex_file( params[ "basename" ] + ".tex", params );

	# open the Makefile
	fid = open( 'Makefile', 'w' );

	# write the Makefile
	write_makefile( fid, params );		# close the makefile
	fid.close();
	return;
#fed main()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
if __name__ == "__main__":
	main();
# __name__ == "__main__"	
#-------------------------------------------------------------------------------