# File Research: sources/os/bsd/openbsd-src/sys/sys/ttydefaults.h

Defines system-wide default terminal flags and control characters. Defaults enable common canonical input, echo, signals, extended processing, output post-processing, and 9600 baud.

If `TTYDEFCHARS` is defined before inclusion, the file emits a `ttydefchars[NCCS]` initializer array and then undefines `TTYDEFCHARS`. This conditional definition pattern is intentional but means the header can emit storage in exactly the translation unit that requests it.
