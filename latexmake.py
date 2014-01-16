#!/usr/bin/python

# ABOUT:
#	A python script I have been working on to make the Makefile for a generic TeX 
#	document. It is probably similar to latexmk [1], but there is something to be
#	said for writing some things yourself
#
# PUBLIC REPOSITORY:
#	
#
# SUGGESTED USE:
#	- Put the git repository on your machine (the location is /path/to/repo)	
#	- In your path (type "echo $PATH" w/o quotes in terminal to see the locatons
#	of path. A further suggestion: add a folder to PATH that does not require root
#	access, e.g, ~/bin), make a link to this file:
#		cd /someplace/in/path
#		ln -s /path/to/repo/latexmake.py latexmake
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


#--------------------------------------------------------------------------------
class latexmake_invalidInput(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_invalidInput(RuntimeError)
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
class latexmake_noInput(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_noInput(RuntimeError)
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
class latexmake_invalidBasename(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_invalidBasename(RuntimeError)
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
class latexmake_nonexistantFile(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_invalidBasename(RuntimeError)
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
class latexmake_invalidArgument(RuntimeError):
   def __init__(self, arg):
      self.args = arg;
# class latexmake_invalidArgument(RuntimeError)
#--------------------------------------------------------------------------------


#================================================================================
#
#		Executable testing code
#
#================================================================================


#--------------------------------------------------------------------------------
def is_exe(fpath):
	# used to see if fpath is an executable
	# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
	return os.path.isfile(fpath) and os.access(fpath, os.X_OK);
# fed is_exe( fpath )
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
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
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
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
#--------------------------------------------------------------------------------


#================================================================================
#
#		Output Messages
#
#================================================================================


#--------------------------------------------------------------------------------
def latexmake_usage():
	output = 'latexmake [options] basefilename\n';
	output += '\t--tex=/path/to/tex compiler\n';
	output += '\t--bib=/path/to/bib compiler\n';
	#output += '\t--nooverwrite\t\t\tWill not overwrite a Makefile\n';
	return output
# fed latexmake_usage()
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def latexmake_copyright():
	output = 'latexmake\n';
	output += '\n\tCopyright 2014 Paul Romanczyk\n';
	return output
# fed latexmake_copyright()
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def latexmake_version():
	output = \
	str( latexmake_version_major ) + '.' + \
	str( latexmake_version_minor ) + '.' + \
	str( latexmake_version_revision );
	return output;
# fed latexmake_version()
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def latexmake_header():
	output = '# Generated by latexmake v' + latexmake_version() + '\n';
	output += '# Created on ' + str( datetime.datetime.utcnow() ) + ' UTC\n';
	return output;
# fed latexmake_header()
#--------------------------------------------------------------------------------


#================================================================================
#
#		helper functions
#
#================================================================================

#--------------------------------------------------------------------------------
def unique( data ):
	output = [];
	for item in data:
		if item not in output:
			output.append( item );
	return output;

# fed unique( data )
#--------------------------------------------------------------------------------


#--------------------------------------------------------------------------------
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
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
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
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
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
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def parseNestedEngine( line, leftIndex, rightIndex ):
	output = [];

	if len( leftIndex ) != len( rightIndex ):
		# TODO raise exception
		pass;
		
		# set up some iterators
	lit = 0;
	rit = 0;

	# set up a stack for left {
	stack = [];

	# parse the string
	run = True;
	print line;
	o = "";
	t = "";
	for i in range( 0, len( line ) ):
		o += str( i % 10 );
		t += str( i / 10 );
	print t;
	print o;
	print;
	it = 0;
	while run:	
		print "New Iter ***********************************"
		print "iteration:", it;
		print "it:\tl:", lit, "\tr:", rit;
		#print "idx:\tl:", leftIndex[ lit ], "\tr:", rightIndex[ rit ];
		print "stack:", stack;
		mes = "";
		if len( stack ) == 0:
			if lit >= len( leftIndex ):
				mes = "11";
				# nothing in stack and no left, stop!
				run = False;
			else:
				mes = "12";
				# nothing in the stack and available left, add left to stack
				stack.append( leftIndex[ lit ] );
				lit += 1;
		# elif rit > lit:
		# 	# TODO raise exception
		# 	pass;
		elif rit >= len( rightIndex ):
			mes = "2";
			run = False;
		else:
			# the stack is not empty

			# check if we have any possible left braces remaining
			if lit + 1 < len( leftIndex ):
				if leftIndex[ lit + 1 ] < rightIndex[ rit ]:
					mes = "311";
					stack.append( leftIndex[ lit ] );
					lit += 1;
				elif leftIndex[ lit ] < rightIndex[ rit ]:
					mes = "312";
					stack.append( leftIndex[ lit ] );
					lit += 1;
				else:
					mes = "313";
					output.append( line[ stack[-1]:rightIndex[ rit ] + 1 ] );
					rit += 1;
					stack.pop();
			else: 
				mes = "33";
				output.append( line[ stack[-1]+1:rightIndex[ rit ] ] );
				rit += 1;
				stack.pop();
		print "message:", mes;
		it += 1;
	return output;
# fed parseNestedEngine( line, leftIndex, rightIndex )
#--------------------------------------------------------------------------------


#--------------------------------------------------------------------------------
def parseDataInSquiglyBraces( line ):
	# find all squiglies
	lidx = [ m.start(0) for m in re.finditer( "{", line ) ];
	ridx = [ m.start(0) for m in re.finditer( "}", line ) ];

	# find any escaped squiglies
	not_lidx = [ m.start(0) + 1 for m in re.finditer( "\\\{", line ) ];
	not_ridx = [ m.start(0) + 1 for m in re.finditer( "\\\}", line ) ];

	# remove any escaped squiglies from lidx
	for i in not_lidx:
		if i in lidx: 
			lidx.remove( i );
		else:
			# TODO raise exception
			pass;

	# remove any escaped squiglies from ridx
	for i in not_ridx:
		if i in ridx: 
			ridx.remove( i );
		else:
			# TODO raise exception
			pass;
	
	# make sure the number of elements in lidx and ridx is the same
	if len( lidx ) != len( ridx ):
		pass;
		# TODO raise exception

	# if there are no squiglies, return an empty list
	if len( lidx ) == 0:
		return [];

	# run the parsing engine
	return parseNestedEngine( line, lidx, ridx );

# fed parseDataInSquiglyBraces( line )
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def parseDataInSquareBraces( line ):
	# TODO: this will not correctly handle {{foo} bar}
	match = re.search( "[.*]", line );
	if match:
		return match.group(0) [1:-1]; 
	else:
		return None;
# fed parseDataInSquareBraces( line )
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def parseDataInParentheses( line ):
	# TODO: this will not correctly handle {{foo} bar}
	match = re.search( "(.*)", line );
	if match:
		return match.group(0) [1:-1]; 
	else:
		return None;
# fed parseDataInParenthesies( line )
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def parseDataInAngleBraces( line ):
	# TODO: this will not correctly handle {{foo} bar}
	match = re.search( "<.*>", line );
	if match:
		return match.group(0) [1:-1]; 
	else:
		return None;
# fed parseDataInAngleBraces( line )
#--------------------------------------------------------------------------------



#================================================================================
#
#		TeX file parsing
#
#================================================================================


#--------------------------------------------------------------------------------
def parseCommaSeparatedData( line ):
	locs = [ (None,0) ];
	for m in re.finditer( "\s*,\s*", line ):
		locs.append( ( m.start(), m.end() ) );
	locs.append( ( len( line), 0 ) );
	output = [];
	for it in range( 0, len( locs ) - 1 ):
		output.append( line[ locs[it][1]:locs[it+1][0] ] );

	return output;
# fed parseCommaSeparatedData( line )
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def removeTeXcomments( texFile ):
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
# fed removeTeXcomments
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def findPackages( texFile ):
	locs = re.findall( '\\usepackage{.*}', texFile );
	packages = [];
	for line in locs:
		package = parseCommaSeparatedData( parseDataInSquiglyBraces( line ) );
		packages += package;
	return packages;
# fed findPackages( texFile )
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def findGraphicsPaths( texFile ):
	locs = re.findall( '\\usepackage{.*}', texFile );
	graphicsPaths = [];
	for line in locs:
		graphicsPath = parseCommaSeparatedData( parseDataInSquiglyBraces( line ) );
		graphicsPaths += graphicsPath;
	return graphicsPaths;
# fed findPackages( texFile )
#--------------------------------------------------------------------------------



#--------------------------------------------------------------------------------
# get any bibliographies, figures, graphics paths, sub tex files
def parse_latex_file( filename ):
	output = {};
	output[ 'tex_files' ] = [];
	output[ 'figures' ] = [];
	output[ 'graphics_paths' ] = [];
	output[ 'bib_files' ] = [];
	output[ 'bib_info' ] = {};
	try:
		fid = open( filename, 'r' );
		if fid < 0:
			raise latexmake_nonexistantFile( filename );

		texFile = fid.read();
		fid.close();

		# TODO: look for latexmk directives here

		# remove the comments
		texFile = removeTeXcomments( texFile );

		# search for packages
		packages = findPackages( texFile );

		# search for included files

		print packages
		
	except latexmake_nonexistantFile, e:
		raise( latexmake_nonexistantFile( e.args ) );
	else:
		return output;

# fed parse_latex_file( file )
#--------------------------------------------------------------------------------


#================================================================================
#
#		Meat and Potatoes
#
#================================================================================


#--------------------------------------------------------------------------------
def latexmake_default_params():
	params = {};
	params[ 'tex_engine' ] = 'pdflatex';
	params[ 'tex_options' ] = '--file-line-error';
	params[ 'bib_engine' ] = 'bibtex';
	params[ 'idx_engine' ] = 'makeindex'
	params[ 'make_bib_in_default' ] = False;
	params[ 'make_index_in_default' ] = False;
	params[ 'basename' ] = '';
	params[ 'basepath' ] = '.';
	params[ 'tex_files' ] = [];
	params[ 'fig_files' ] = [];
	params[ 'bib_files' ] = [];
	params[ 'output_extension' ] = [ 'pdf' ];
	params[ 'graphics_paths' ] = [];
	params[ 'has_git' ] = functionExists( 'git' );
	params[ 'has_latex2rft' ] = functionExists( 'latex2rtf' );
	return params;
# fed latexmake_default_params()
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
def write_makefile( fid, options ):
	# write the engines
	fid.write( "TEX_ENGINE=" + options[ "tex_engine" ] + '\n' );
	fid.write( "TEX_OPTIONS=" + options[ "tex_options" ] + '\n' );
	fid.write( "BIB_ENGINE=" + options[ "bib_engine" ] + '\n' );
	fid.write( "IDX_ENGINE=" + options[ "idx_engine" ] + '\n' );
	fid.write( "\n" );
	fid.write( "SOURCE=" + options[ "basename" ] + '\n' );
	fid.write( "TEX_FILES=" );
	for f in options[ 'tex_files']:
		pth = os.path.relpath( f );
		fid.write( " " + pth );
	fid.write( "\n" );
	fid.write( "BIB_FILES=")
	fid.write( "\n" );
	fid.write( "FIG_FILES=")
	fid.write( "\n\n" );

	fid.write( "\n\n" );
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
			pass;
			# TODO: add index engine
	fid.write( "\tmake -e ${SOURCE}." + exts[ 0 ] + "\n" );

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

	# final is the last 2 latex complies
	fid.write( "\n\n" );
	fid.write( "# final is the last 2 latex complies\n" );
	fid.write( '.PHONY: final\n');
	fid.write( 'final: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n');
	fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );
	fid.write( "\t${TEX_ENGINE} ${TEX_OPTIONS} ${SOURCE}.tex\n" );


	# clean
	fid.write( "\n\n" );
	fid.write( "# clean auxiliary files\n" );
	fid.write( '.PHONY: clean\n');
	fid.write( 'clean:\n');
	writeLongLines( fid, "rm -rf *.aux *.toc *.log *.lof *.lot " + \
		"*.synctex.gz *.bbl *.blg *.bcf *.run.xml *-blx.bib *.nav *.vrb " + \
		"*snm *.out *.fls *.fdb_latexmk", 80, 8, 1, False );

	fid.write( "\t\n" );

	# cleanall
	fid.write( "\n\n" );
	fid.write( "# clean all output files\n" );
	fid.write( '.PHONY: cleanall\n');
	fid.write( 'cleanall:\n');
	fid.write( "\trm -rf" );
	for ext in [ "dvi", "ps", "eps", "pdf" ]:
		fid.write( " ${SOURCE}." + ext );
	fid.write( "\n" );
	fid.write( "\tmake -e clean\n" );	

	# clean general
	fid.write( "\n\n" );
	fid.write( "# clean general auxiliary files\n" );
	fid.write( '.PHONY: cleangeneral\n');
	fid.write( 'cleangeneral:\n');
	fid.write( "\trm -rf *.aux *.toc *.log *.lof *.lot\n" );	

	# clean beamer
	fid.write( "\n\n" );
	fid.write( "# clean beamer auxiliary files\n" );
	fid.write( '.PHONY: cleanbeamer\n');
	fid.write( 'cleanbeamer:\n');
	fid.write( "\trm -rf *.aux *.log *.toc *.nav *.vrb *snm *.out\n" );	

	# clean bib
	fid.write( "\n\n" );
	fid.write( "# clean bibliography auxiliary files\n" );
	fid.write( '.PHONY: cleanbib\n');
	fid.write( 'cleanbib:\n');
	fid.write( "\trm -rf *bbl *.blg *.bcf *.run.xml *-blx.bib\n" );	

	if options[ "has_latex2rft" ]:
		fid.write( "\n\n" );
		fid.write( "# make rtf file\n" );
		fid.write( "${SOURCE}.rtf: ${TEX_FILES} ${BIB_FILES} ${FIG_FILES}\n" );
		fid.write( "\tlatex2rtf -M32 ${SOURCE}.tex\n" );


	if options[ "has_git" ]:
		# git backup with message 'bkup'
		fid.write( "\n\n" );
		fid.write( "# git backup\n" );
		fid.write( ".PHONY: gitbkup\n" );
		fid.write( "gitbkup: .git .gitignore\n" );
		fid.write( "\tgit add -A\n" );
		fid.write( "\tgit commit -m 'bkup'\n" );
		

		# git init ( so make gitbkup does not throw error if not a repository )
		fid.write( "\n\n" );
		fid.write( "# git init\n" );
		fid.write( ".git:\n" );
		fid.write( "\tgit init\n" );
		

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
		fid.write( "\techo '*.aux' >> .gitignore\n" );
		fid.write( "\techo '*.toc' >> .gitignore\n" );
		fid.write( "\techo '*.lof' >> .gitignore\n" );
		fid.write( "\techo '*.lot' >> .gitignore\n" );
		fid.write( "\techo '*.lof' >> .gitignore\n" );
		fid.write( "\techo '*.log' >> .gitignore\n" );
		fid.write( "\techo '*.synctex.gz' >> .gitignore\n" );
		fid.write( "\techo '' >> .gitignore\n" );
		fid.write( "\techo '# beamer auxiliary files' >> .gitignore\n" );
		fid.write( "\techo '*.nav' >> .gitignore\n" );
		fid.write( "\techo '*.vrb' >> .gitignore\n" );
		fid.write( "\techo '*.snm' >> .gitignore\n" );
		fid.write( "\techo '*.out' >> .gitignore\n" );
		fid.write( "\techo '' >> .gitignore\n" );
		fid.write( "\techo '# bibliography auxiliary files' >> .gitignore\n" );
		fid.write( "\techo '*.bbl' >> .gitignore\n" );
		fid.write( "\techo '*.blg' >> .gitignore\n" );
		fid.write( "\techo '*.run.xml' >> .gitignore\n" );
		fid.write( "\techo '*-blx.bib' >> .gitignore\n" );
		fid.write( "\techo '' >> .gitignore\n" );
		fid.write( "\techo '# latexmk auxiliary files' >> .gitignore\n" );
		fid.write( "\techo '*.fdb_latexmk' >> .gitignore\n" );
		fid.write( "\techo '*.fls' >> .gitignore\n" );
		fid.write( "\techo '# converted figures' >> .gitignore\n" );
		fid.write( "\techo '*-converted-to.pdf' >> .gitignore\n" );
		for fig in options[ "fig_files" ]:
			( pth, fig ) = os.path.split( fig );
			pth = os.path.join( pth, "*-converted-to.pdf" );
			fid.write( "\techo '" + pth + "' >> .gitignore\n" );
		fid.write( "\techo '' >> .gitignore\n" );
		fid.write( "\techo '# mac things' >> .gitignore\n" );
		fid.write( "\techo '.DS_STORE' >> .gitignore\n" );



	return;
# fed write_makefile( fid )
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
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

		output[ "tex_files" ].append( tmp )

		if idx < 0:
			raise latexmake_invalidBasename( tmp );
		else:
			tmp = tmp[ :idx ]
		output[ 'basename' ] = tmp;

		for arg in args[1:-1]:
			#print arg
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
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
"""
def main():
	try:
		# parse the parameters
		params = latexmake_parse_inputs();

		# open the Makefile
		fid = open( 'Makefile', 'w' );
		# write the Makefile
		write_makefile( fid, params );
		# close the makefile
		fid.close();
	except latexmake_nonexistantFile, e:
		print "the file", e.args, "does not exist."
	except latexmake_noInput, e:
		print latexmake_usage();
		return;
	except latexmake_invalidBasename, e:
		print e.args, 'Is not a valid LaTeX file';
		return;
	except Exception, e:
		print 'Unknown error in main():';
		print e;
"""
#--------------------------------------------------------------------------------
def main():

	# parse the parameters
	params = latexmake_parse_inputs();
	
	foo = parse_latex_file( params[ "basename" ] + ".tex" );

	# open the Makefile
	fid = open( 'Makefile', 'w' );

	# write the Makefile
	write_makefile( fid, params );		# close the makefile
	fid.close();
#fed main()
#--------------------------------------------------------------------------------


if __name__ == "__main__":
	main();