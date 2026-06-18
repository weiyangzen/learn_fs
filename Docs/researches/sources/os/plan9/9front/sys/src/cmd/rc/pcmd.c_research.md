# File Research: sources/os/plan9/9front/sys/src/cmd/rc/pcmd.c

Pretty-printer for parse trees. `pcmd()` recursively emits textual `rc` syntax for every tree type: pipelines, redirections, functions, loops, conditionals, assignments, backquotes, subshells, lists, and words.

Used for function serialization, debugging, and `whatis`. It deglobs unquoted words for display and quotes quoted words with shell quoting rules.

Also renders here-doc bodies after their redirection syntax.
