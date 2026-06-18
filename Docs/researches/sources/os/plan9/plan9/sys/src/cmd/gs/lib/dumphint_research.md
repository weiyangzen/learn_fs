# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/dumphint

Shell wrapper for formatting linearized PDF hint data.

Behavior:

- Initializes `GS_EXECUTABLE=gs`.
- Accumulates leading `-*` options into `OPTIONS`, defaulting to `-dSAFER -dDELAYSAFER`.
- Requires exactly one `input.pdf`.
- Executes Ghostscript in quiet no-display mode over `dumphint.ps`.

This is command-line glue for a Ghostscript PostScript utility.
