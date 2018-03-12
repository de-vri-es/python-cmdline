from argparse import Namespace

from .types import Option, PositionalParameter


def split_assignments(arguments):
	""" Iterate over the given arguments, splitting assignments into separate arguments.

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
		self._positionals   = positionals or []
		self._options       = options     or []
		self._option_index  = index_options(self._options)
		self.reset()

	def reset(self):
		self._positionals_parsed = 0
		self._parsed             = {}

	def set_defaults(self, namespace, force=False):
		""" Set the default values for each option in the given namespace. """
		for option in self._positionals:
			if force or not hasattr(namespace, option.dest):
				setattr(namespace, option.dest, option.default)


	def parse_child(self, arguments):
		""" Parse a single option from the argument list. """
		if not arguments: return None, None, [], arguments

		# Try an option.
		child = self._option_index.get(arguments[0])

		# Try a positional parameter.
		if not child:
			if self._positionals_parsed >= len(self._positionals):
				return None, None, [], arguments
			child = self._positionals[self._positionals_parsed]
			self._positionals_parsed += 1

		value, consumed, remaining = child.parse(arguments)
		return child, value, consumed, remaining

	def parse(self, arguments, namespace=None):
		""" Parse all arguments.

		Calls parse_one() untill all arguments are parsed or an error occurs.

		An error will be raised if:
		  - parse_one() raises an error
		  - no more arguments can be parsed but the remaining argument list is not empty

		Return: the parsed namespace
		"""
		namespace = namespace or Namespace()
		while arguments:
			option, value, _, arguments = self.parse_child(arguments)
			print(option, value, _, arguments)
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
