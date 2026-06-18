# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/include.c

`#include` and line-directive support for `cpp`.

`doinclude` parses quoted and angle-bracket includes, expands macro-derived include names when needed, searches absolute paths, configured include directories, and finally the current source directory, then pushes the opened file as a new `Source`. With `-M`, it emits dependency lines using the object name from `setobjname`.

`genline` writes `#line` directives using the current file and working directory unless `-P` disabled line info.
