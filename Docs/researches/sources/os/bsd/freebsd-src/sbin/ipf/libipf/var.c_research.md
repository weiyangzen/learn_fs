# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/var.c

Simple variable store and `$variable` expansion engine for IPFilter config parsing.

Key behavior:
- Maintains a linked list of name/value variables.
- `set_variable()` creates or replaces variables and strips matching single/double quotes around values.
- `get_variable()` parses `$name` or `${name}` references and recursively expands the stored value.
- `expand_string()` replaces embedded variables, supports `$$` escaping, and allocates expanded strings when needed.

Research notes:
- No cycle detection for recursive variables.
- `set_variable()` mutates quoted input values by writing a NUL before the closing quote.
