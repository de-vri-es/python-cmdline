class Option:
	def __init__(self, names, nargs=1, implicit=None, default=None, repeated=False, required=False, type=None, metavar=None, help=None):
		if isinstance(names, str): names = [names]

		self.names      = names
		self.nargs      = nargs
		self.implicit   = implicit
		self.default    = default
		self.repeated   = repeated
		self.required   = required
		self.type       = type

		if self.nargs == 1:
			self.metavars = [metavar] if metavar is not None else ['VALUE']
		else:
			self.metavars = metavar if metavar is not None else ['VALUE'] * self.nargs
		self._help = help

	def usage(self):
		if self.required:
			return ' '.join(self.names + self.metavars)
		else:
			return '[{}]'.format(' '.join(self.names + self.metavars))

	def help(self):
		return ' '.join(self.names + self.metavars), self._help

	def __convert(self, arguments):
		if self.nargs == 0:
			return self.implicit
		elif self.nargs == 1:
			return self.type(arguments[0]) if self.type else arguments[0]
		else:
			return self.type(arguments) if self.type else arguments

	def parse(self, arguments):
		if not arguments:
			return [], arguments, None

		name = arguments[0]
		if name not in self.names:
			return [], arguments, None

		if len(arguments) < self.nargs + 1:
			raise RuntimeError('not enough arguments for option {}: expected {}, got {}'.format(name, self.nargs, len(arguments) - 1))

		consumed  = arguments[:self.nargs + 1]
		remaining = arguments[self.nargs + 1:]
		return self.__convert(consumed[1:]), consumed, remaining


def flag(names, inverted=False, help=None):
	return Option(names, nargs=0, implicit=not inverted, default=inverted, help=help)


class PositionalParameter:
	def __init__(name, repeated=False, required=False, type=None, metaver=None, help=None):
		self.name     = name
		self.repeated = repeated
		self.required = required
		self.type     = type

		self._metavar = metavar if metavar is not None else name.upper()
		self._help    = help

	def usage(self):
		if self.required and self.repeated:
			return '{}...'.format(self._metavar)
		elif self.required:
			return self._metavar
		elif self.repeated:
			return '[{}...]'.format(self._metavar)
		else:
			return '[{}]'.format(self._metavar)

	def help(self):
		return self._metavar, self._help

	def __convert(self, arguments):
		return self.type(arguments) if self.type else arguments

	def parse(self, arguments):
		if not arguments:
			return None, [], arguments
		consumed  = arguments[:1]
		remaining = arguments[1:]
		return self.__convert(consumed[0]), consumed, remaining
