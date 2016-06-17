#!/usr/bin/env python
# forcegps.py
# AB2Tech
# Austin Beam
# Alan Bullick
# 2016-05

# This script adds GPS EXIF tags, if none are populated, for an image based on a
# timezone or timezone alias (as defined in the script). Default timezone
# locations should always be over a body of water (to remind us they aren't
# *real* GPS tags).
#
# http://www.kansas.com/news/local/article71260267.html
#
# The script's primary application is to enable proper image ordering upon
# upload into a Google Photos album. Google Photos uses an image's GPS data to
# determine the timezone in which the image was created. If no GPS tags are
# populated, Google Photos defaults to using the timezone of the IP address
# where the image was uploaded. This becomes an issue when images from multiple
# sources and/or upload locations (user sharing) are uploaded to the same album.
# This method is more straightforward solution than VPN uploading from the
# correct time zone.
#
# There could be other applications for this as well...
#
# TODO there are many ways to make this script more pythonic, but as-is this was
# a quick hack to save us some time and pain...feel free to help us make it
# better and/or more useful.
#
# FYI - Google has recently added batch date editing, which is awesome, but we
# feel like this still has its place for cleaning things up at the source.
# Hopefully it can be useful to others also.

# Import python module dependencies
try:
  import logging
except ImportError:
  print 'Unable to import logging module'
  raw_input('Press Enter to continue...')
  raise SystemExit, 1

# Configure logging for the default basic configuration
logging.basicConfig()
# Create a logging object called log
log = logging.getLogger(__name__)
# Configure default log level
#log.setLevel(logging.DEBUG)
log.setLevel(logging.ERROR)

# Print log level if DEBUG or lower is enabled
log.info('Debug level: ' + str(log.getEffectiveLevel()))

# Import required modules
import_success_flag = True

module = 'argparse '
try:
  import argparse
  log.info(module + 'module loaded')
except ImportError:
  log.exception(module + 'module failed to Load')
  import_success_flag = False

module = 'itertools->imap '
try:
  from itertools import imap
  log.info(module + 'module loaded')
except ImportError:
  log.exception(module + 'module failed to load')
  import_success_flag = False

module = 'os '
try:
  import os
  log.info(module + 'module loaded')
except ImportError:
  log.exception(module + 'module failed to Load')
  import_success_flag = False

module = 're '
try:
  import re
  log.info(module + 'module loaded')
except ImportError:
  log.exception(module + 'module failed to Load')
  import_success_flag = False

module = 'string '
try:
  import string
  log.info(module + 'module loaded')
except ImportError:
  log.exception(module + 'module failed to Load')
  import_success_flag = False

module = 'subprocess '
try:
  import subprocess
  log.info(module + 'module loaded')
except ImportError:
  log.exception(module + 'module failed to Load')
  import_success_flag = False

if not import_success_flag:
  log.error('module(s) failed to load')
  raw_input('Press Enter to continue...')
  raise SystemExit, 1
log.info('')

# Function for capturing the full executable path of a program
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def isValidFile(parser, arg):
  if not os.path.isfile(arg):
    parser.error('The file %s does not exist!' % arg)
  else:
    return arg

# Create an argument parser
parser = argparse.ArgumentParser(
  description='force GPS coordinates for the specified files')
parser.add_argument('filename', nargs='*',
  help='filename of an image')
parser.add_argument('-a', '--alias',
  help='location alias (list defined in application)')
parser.add_argument('-c', '--coordinates', type=float, nargs=2,
  metavar=('LAT','LONG'),
  help='manually enter coordinates (decimal format, separated by space)')
parser.add_argument('-f', '--force', action='store_true',
  help='force modification of all listed files (default is to ignore files \
with existing coordinates)')
parser.add_argument('-l', '--list_aliases', action='store_true',
  help='list all available aliases and exit')
parser.add_argument('-n', '--do_nothing', action='store_true',
  help='do nothing (useful with -v to preview files to be edited')
parser.add_argument('-o', '--overwrite', action='store_true',
  help='overwrite original file(s) with edits (CAUTION)')
parser.add_argument('-s', '--source_file', type=lambda x: isValidFile(parser,x),
  help='source coordinates from a file')
parser.add_argument('-v', '--verbose', action='append_const', const = 1,
  help='verbose output -- each \'v\' increases verbosity')
args = parser.parse_args()

# Use the verbosity level to determine the log level. Log WARNING by default,
# but go to lower levels as requested. Each verbosity 'v' will move down the
# list one iteration. Maximum verbosity is DEBUG (-vv).
# Level     Numeric value
# WARNING   30
# INFO      20
# DEBUG     10
# Set verbosity based on user input
verbosity = 0 if args.verbose is None else sum(args.verbose)
# Don't let verbosity drive us below DEBUG
if verbosity > 2:
  verbosity = 2
# Set the logging level
log.setLevel(logging.WARNING - (verbosity * 10))

alias_dict = dict()
# Alias definitions should be *all lowercase*, but script arguments can be any
# case (we force arguments to lowercase later)
alias_dict['chicago']                  = [41.879421, -87.523448]
alias_dict['dallas']                   = [32.832799, -96.721661]
alias_dict['eiffel']                   = [48.858554, 2.294513]
alias_dict['england']                  = [55.183517, -2.506142]
alias_dict['france']                   = [46.735221, 2.479992]
alias_dict['germany']                  = [50.141989, 7.169835]
alias_dict['la']                       = [34.045013, -118.229554]
alias_dict['london']                   = [51.506982, -0.119185]
alias_dict['los angeles']              = [34.045013, -118.229554]
alias_dict['midland']                  = [32.007821, -102.086352]
alias_dict['nevada']                   = [38.954167, -120.100472]
alias_dict['paris']                    = [48.854915, 2.351727]
alias_dict['rome']                     = [41.902129, 12.468794]
alias_dict['seagraves']                = [32.939237, -102.565286]
alias_dict['tahoe']                    = [38.954167, -120.100472]
alias_dict['texas']                    = [31.141359, -99.420637]
alias_dict['tx']                       = [31.141359, -99.420637]
alias_dict['uk']                       = [55.183517, -2.506142]

# List aliases '-l' '--list-aliases'
max_alias_len = max(imap(len, alias_dict))
if args.list_aliases:
  for key in sorted(alias_dict):
    print '{:>{width}}: {:}'.format(
      key.upper(), str(alias_dict[key]), width=max_alias_len)
  raise SystemExit, 0

# Find exiftool in the path or tell the user they don't have it
exiftool = which('exiftool')
if exiftool is None:
  log.exception('Unable to find exiftool. Is it installed and in your path?')
  raise SystemExit, 1

# Figure out how coordinates were specified by the user. Aliases will always be
# taken over anything else. TODO consider making this warn the user if they
# specify coordinates by multiple arguments.
if args.alias is not None:
  coordinates = alias_dict.get(args.alias.lower())
elif args.coordinates is not None:
  coordinates = args.coordinates
elif args.source_file is not None:
  coordinates = None
  exiftool_call = \
      [exiftool, '-m', '-s', '-s', '-s', '-GPSLatitude', args.source_file]
  latitude = subprocess.check_output(exiftool_call,
                                     stderr=subprocess.STDOUT).strip()
  log.debug('Extracted latitude ' + latitude + ' from source file "' + \
            args.source_file + '"')
  exiftool_call = \
      [exiftool, '-m', '-s', '-s', '-s', '-GPSLongitude', args.source_file]
  longitude = subprocess.check_output(exiftool_call,
                                      stderr=subprocess.STDOUT).strip()
  log.debug('Extracted longitude ' + longitude + ' from source file "' + \
            args.source_file + '"')
elif args.do_nothing:
  # You may all do nothing, I'll go to Texas!
  #     - If Davy Crockett wrote our comments...
  coordinates = alias_dict.get('tx') # just minimizing later conditionals
#elif args.search is not None:
#  TODO add if possible
#  print 'Go search for coordinates'
else:
  print 'Coordinates not specified'
  raise SystemExit, 1

if args.do_nothing:
  log.warning('Doing nothing as requested...')

if coordinates is not None:
  log.info('Configuring GPS to: ' + str(coordinates))
  # Extract the lat/long from the specified coordinates
  try:
    latitude = coordinates[0]
    longitude = coordinates[1]
  except NameError:
    print 'Coordinates not specified'
    raise SystemExit, 1
  except TypeError:
    print 'Coordinates not specified -- check argument order'
    raise SystemExit, 1

  # Define the lat/long reference directions based on +/-
  if latitude > 0:
    latref = 'N'
  else:
    latref = 'S'

  if longitude > 0:
    lonref = 'E'
  else:
    lonref = 'W'

  # Now that we've checked for reference direction, make lat/long into printable
  # strings (we'll need them to pass to exiftool)
  latitude = str(latitude)
  longitude = str(longitude)
elif latitude is not None:
  # Need to define the references and drop them from the lat/long
  latref = latitude[-1:]
  lonref = longitude[-1:]
  latitude = latitude[:-1].strip()
  longitude = longitude[:-1].strip()
  log.info('Configuring GPS to: ' + latitude.strip() + ", " + longitude.strip())
else:
  print 'Coordinates not specified'
  raise SystemExit, 1


# Figure out which files need coordinates added unless we're forced to add them
# to all images with the '-f' / '--force' flag
if not args.force:
  file_list = []
  for arg in args.filename:
    if os.path.exists(arg):
      # build the exiftool call string
      exiftool_call = [exiftool, '-m', '-s', '-GPSLatitude', '-GPSLongitude', arg]
      log.debug('exiftool_call: ' + str(exiftool_call))
      # TODO not ideal to call this for every file, but for now it's the easiest
      # way to get the job done
      exiftool_out = \
          subprocess.check_output(exiftool_call, stderr=subprocess.STDOUT)
      log.debug('exiftool_out:\n' + exiftool_out)
      # remove all whitespace because we need to see if these GPS tags exist
      exiftool_out = exiftool_out.translate(None, string.whitespace)

      # if nothing was output, the tags don't exist and this file needs to be
      # updated with GPS tags
      if not exiftool_out:
        file_list.append(arg)
        log.info('adding file: ' + arg)
      else:
        log.debug('ignoring file: ' + arg)
    else:
      log.exception('Invalid filename specified: "' + arg + '"')
      raise SystemExit, 1
else:
  file_list = args.filename

# Log the final list of files to edit
log.debug(file_list)

# Only proceed if there are files to edit and we're doing something (i.e. not
# doing nothing)
if file_list and not args.do_nothing:
  # build the exiftool call
  exiftool_call = [exiftool,
                   '-m', # Ignore warnings and minor errors
                   '-preserve', # Preserve the original file time
                   '-GPSLatitude=' + latitude,
                   '-GPSLongitude=' + longitude,
                   '-GPSLatitudeRef=' + latref,
                   '-GPSLongitudeRef=' + lonref] + file_list

  # add the overwrite flag to the call if overwrite is specified
  if args.overwrite is True:
    exiftool_call += ['-overwrite_original']

  log.debug('exiftool_call: ' + str(exiftool_call))

  subprocess.call(exiftool_call, stderr=subprocess.STDOUT)
  raise SystemExit, 0
else:
  print 'Nothing to do...'
  raise SystemExit, 0
