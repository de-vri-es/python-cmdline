import sys
import os.path

def program_name(path = None):
	if path is None:
		path = sys.argv[0]
	return os.path.basename(path)

def format_usage(name=None, options=None, positionals=None):
	if name        is None: name        = program_name()
	if options     is None: options     = []
	if positionals is None: positionals = []

	options     = ' '.join(map(lambda x: x.usage(), options))
	positionals = ' '.join(map(lambda x: x.usage(), positionals))
	return 'usage: {name} {options} {positionals}'.format(name=name, options=options, positionals=positionals)

def format_options(options, indent='    '):
	options = [x.help() for x in options]
	width   = max(map(lambda x: len(x[0]), options))

	for option in options:
		usage, help = option
		if not help:
			yield indent + usage
		else:
			yield '{indent}{usage:{width}}{seperator}{help}'.format(width=width, usage=usage, help=help, indent=indent, seperator='    ')

def format_help(name=None, options=None, positionals=None):
	yield format_usage(name=name, options=options, positionals=positionals)

	if positionals:
		yield ''
		yield "Positional parameters:"
		yield from format_options(positionals)

	if options:
		yield ''
		yield "Options:"
		yield from format_options(options)
