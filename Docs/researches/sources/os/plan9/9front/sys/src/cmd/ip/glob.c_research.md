# File Research: sources/os/plan9/9front/sys/src/cmd/ip/glob.c

Custom glob implementation used by FTP tools. It builds a linked list of matches without fixed path-element limits, converting `*` and `?` per path component into regular expressions.

`glob` initializes absolute or relative matching, `globnext` recursively expands components, `globdir` scans directories, `globdot` handles `.` directory matches, and `globiter` returns allocated match strings one at a time.

Comment notes this implementation is likely slower than rc globbing but avoids size limits.
