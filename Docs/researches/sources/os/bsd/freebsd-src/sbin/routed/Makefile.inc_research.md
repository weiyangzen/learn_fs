# File Research: sources/os/bsd/freebsd-src/sbin/routed/Makefile.inc

Purpose: small include file for routed-related subdirectories.

Behavior:
- Sets `PACKAGE=rip`.
- Includes parent `../Makefile.inc`.

Integration: shares package classification and parent build settings with `routed` subcomponents such as `rtquery`.

Risk notes: minimal file; behavior depends entirely on the parent include.
