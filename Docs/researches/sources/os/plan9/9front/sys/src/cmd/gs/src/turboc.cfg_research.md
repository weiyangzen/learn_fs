# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/turboc.cfg

Tiny Borland/Turbo C compiler warning configuration file.

Key points:
- Contains five lines of command-line warning switches.
- Disables or adjusts many Turbo C warning classes, including duplicate, return, structure, unused, ambiguous, conversion, and pointer-related diagnostics.
- Ends with `-N`, a Turbo C option.

Dependencies and interactions:
- Intended for old Borland/Turbo C builds rather than the Unix/Plan 9 build path.
- No source code symbols are defined here.

Research relevance:
- Historical build-support artifact for legacy PC compiler compatibility in the Ghostscript source tree.
