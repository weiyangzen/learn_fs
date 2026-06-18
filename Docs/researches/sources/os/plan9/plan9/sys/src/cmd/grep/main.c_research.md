# File Research: sources/os/plan9/plan9/sys/src/cmd/grep/main.c

This file implements `grep` command-line handling and the search loop. It supports flags `bchiLlnsv`, `-e pattern`, and `-f patternfile`, builds the regex, initializes the DFA state, and searches stdin or files.

`search` reads chunks into the shared buffer, simulates a final newline for files without one, advances the DFA byte by byte, and emits/counts lines on newline boundaries. It handles file prefixes, line numbers, count-only, status-only, matching/nonmatching file names, inverse matching, buffering, and ASCII case folding.

The lazy transition cache calls `increment` when a state lacks a transition for the current byte.
