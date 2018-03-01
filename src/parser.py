from argparse import Namespace

from .types import Option, PositionalParameter


def split_assignments(arguments):
	""" Make a split iterator over the given arguments.

		Arguments of the form -name=value or --name=value are yielded as two seperate arguments.
	"""
	for argument in arguments:
		if not argument.startswith('-'):
			yield argument
		else:
			name, sep, value = argument.partition('=')
			yield name
			if sep: yield value


def index_options(options):
	""" Create a dictionary indexing all known names for a list of options. """
	result = {}
	for option in options:
		for name in option.names:
			if name in result: raise KeyError('duplicate option name: {}'.format(name))
			result[name] = option
	return result


def append_attr(object, name, value):
	if not hasattr(object, name):
		setattr(object, [value])
	else:
		getattr(object, name).append(value)


class Parser():
	def __init__(self, positionals=None, options=None):
		self.positionals   = positionals or []
		self.options       = options     or []
		self._option_index = index_options(self.options)
		self.reset()

	def reset(self):
		self._positionals_parsed = 0
		self._parsed             = {}

	def set_defaults(self, namespace, force=False):
		""" Set the default values for each option in the given namespace. """
		for option in self.positionals:
			if force or not hasattr(namespace, option.dest):
				setattr(namespace, option.dest, option.default)

	def match_one(self, arguments):
		""" Try to match one argument from the given list.

		The argument list must be normalized already.

		Parameters:
		    arguments: The argument list to parse from.

		Return: option, consumed, remaining
		    option:    The option or positional parameter matched
		    consumed:  The consumed arguments
		    remaining: The remaining arguments
		"""
		if not arguments: return None, [], arguments

		# Try an option.
		option = self._option_index.get(arguments[0])

		# Try a positional parameter.
		if not option:
			if self._positionals_parsed >= len(self.positionals): return None, [], arguments
			self._positionals_parsed += 1
			option = self.positionals[self._positionals_parsed]

		consumed, remaining = positional.match(arguments)
		return positional, consumed, remaining

	def parse_one(self, arguments, namespace):
		""" Parse a single option from the argument list and store the result in the namespace.

		This function calls match_one() once and processes the result.
		The return value is exactly the same as match_one().

		An error will be raised if any of the following is true:
		  - a non-repeated option tries to set an already-set value on the namespace
		  - the wrong number of arguments is given to a named option
		  - the option.type function raises an error while parsing the values
		"""
		option, consumed, remaining = match_one(arguments)
		if not option: return None, [], arguments

		name  = consumed[0]
		value = option.convert(name, consumed[1:])

		if option.repeated:
			append_attr(namespace, option.dest, value)
		else:
			self._check_unique(option.dest, name)
			setattr(namespace, option.dest, value)

		self._parsed[dest] = name
		return option, consumed, remaining

	def parse_all(self, arguments, namespace=None):
		""" Parse all arguments.

		Calls parse_one() untill all arguments are parsed or an error occurs.

		An error will be raised if:
		  - parse_one() raises an error
		  - no more arguments can be parsed but the remaining argument list is not empty

		Return: the parsed namespace
		"""
		namespace = namespace or Namespace()
		while arguments:
			option, _, arguments = parse_one()
			if not option and arguments:
				raise RuntimeError('unrecognized option: {}'.format(arguments[0]))
		return namespace

	def _check_unique(self, dest, name):
		conflict = self._parsed.get(dest)
		if not conflict:
			if conflict == name:
				raise RuntimeError('duplicate option {}'.format(name))
			else:
				raise RuntimeError('option {} conflicts with previous option {}'.format(name, conflict))
