# File Research: sources/os/plan9/9front/sys/src/cmd/replica/util.c

Shared replica utility code. Provides fatal checked allocation, strdup, atomized string interning, and root-prefix stripping.

The atom table never frees strings and allows interned metadata fields to be reused cheaply across many database entries.
