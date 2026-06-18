# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpcmp.c

Compares multiprecision integers.

Key functions:
- `mpmagcmp`: compares magnitudes by limb count then limb values.
- `mpcmp`: signed comparison, reversing magnitude order for negative values.

Dependency:
- Uses low-level `mpveccmp`.
