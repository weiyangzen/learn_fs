# sources/test-tools/strace/maint/errnoent.sh

Purpose: converts preprocessor errno definitions into indexed C initializer entries for strace errno tables.

Important APIs/types/functions: one awk program reads `#define E... <number>` lines, stores `errno[number] = name`, tracks `max`, and prints array slots as `[ n ] = "ENAME",`.

Control flow: all input files are processed by awk; matching definitions update the map and maximum numeric value. The END block emits all present entries from 0 through `max`.

State and persistence behavior: no persistent writes; output is stdout. Duplicate errno numbers are overwritten by later input definitions.

Dependencies and integration points: used for architecture-specific errno table generation from kernel or libc headers; output integrates with strace's architecture errno lookup headers.

Risks: only simple numeric `#define` values are accepted; aliases, expressions, negative values, or macro indirection are ignored. Input order affects duplicates.

Test signals: generated errno tables should include expected numeric names, build successfully, and match runtime errno decoding tests for target architectures.
