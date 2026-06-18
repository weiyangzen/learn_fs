# File Research: sources/os/plan9/plan9/sys/src/cmd/cleanname.c

Small command wrapper around Plan 9 `cleanname`. Optional `-d pwd` prefixes relative names with a supplied directory before cleaning; absolute paths or no `-d` are cleaned in place. Prints one normalized path per argument.

Handles allocation failure for prefixed names and exits usage on missing args or malformed options.
