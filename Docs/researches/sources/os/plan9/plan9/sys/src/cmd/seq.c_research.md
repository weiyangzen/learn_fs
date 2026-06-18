# File Research: sources/os/plan9/plan9/sys/src/cmd/seq.c

Numeric sequence generator.

Key behavior:
- Parses `seq [-fformat] [-w] [first [incr]] last`.
- Defaults to first `1.0`, increment `1.0`, and `%g\n`.
- `-f` supplies a printf-style format, adding a newline if absent.
- `-w` builds a constant-width decimal format and replaces leading spaces with zeroes.
- Handles positive and negative increments.

Important details:
- Rejects zero increment.
- Width inference refuses exponential `%g` forms.
- Uses double arithmetic for sequence values.

Filesystem relevance:
- None directly; stdout-only command.
