class Option:
	def __init__(names, dest=None, nargs=1, implicit=None, default=None, repeated=False, type=None):
		if isinstance(names, str): names = [names]
		if dest is None: dest = names[0].lstrip('-').replace('-', '_')

		self.names      = names
		self.dest       = dest
		self.nargs      = nargs
		self.implicit   = implicit
		self.default    = default
		self.repeated   = repeated
		self.type       = type or lambda x: x

	def match(self, arguments):
		end = self.nargs + 1
		return argument[:end], arguments[end:]

	def convert(self, name, arguments):
		if len(arguments) != self.nargs:
			raise RuntimeError('wrong number of arguments for option {}: expected {}, got {}'.format(name, self.nargs, len(arguments)))
		if self.nargs == 0:
			return self.implicit
		elif self.nargs == 1:
			return self.type(arguments[0])
		else:
			return self.type(arguments)


def flag(names, dest=None, inverted=False):
	return Option(names, dest=dest, nargs=0, implicit=not inverted, default=inverted)


class PositionalParameter:
	def __init__(name, repeated=False, type=None):
		self.name     = name
		self.repeated = repeated
		self.type     = type or lambda x: x

	def match(self, arguments):
		return argument[:1], arguments[1:]

	def convert(self, name, arguments):
		if len(arguments) != 1:
			raise RuntimeError('wrong number of arguments for positional parameter {}: expected 1, got {}'.format(name, len(arguments)))
		if self.nargs == 0:
			return self.implicit
		elif self.nargs == 1:
			return self.type(arguments[0])
		else:
			return self.type(arguments)

