# File Research: sources/os/plan9/9front/sys/src/cmd/grep/main.c

Command-line and search loop for Plan 9 `grep`. It parses standard flags plus `-e` and `-f`, compiles patterns into the lazy DFA, then searches stdin, one file, or multiple files with filename prefixes.

`search` reads chunks, preserves prior line data across reads, synthesizes a final newline for unterminated files, uses a fast normal loop or ignore-case loop, and emits matching lines/counts/list results according to flags. It flushes periodically and exits success when any match is found.
