# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfinp.h

Purpose: declarations for TrueType reader input helpers.

Key contents:
- Declares byte, signed byte, unsigned/signed short, unsigned int, and signed int reader helpers.

Dependencies: requires `ttfReader` type from `ttfoutl.h`.

Integration notes: small API boundary between abstract font data access and parser code.

Risks: must be included after `ttfReader` is declared.
