# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfstat/Makefile

## Purpose
Builds the `ipfstat` utility.

## Main Elements
- Defines `NOGCCERROR`.
- Sets `PACKAGE=ipf`, `PROG=ipfstat`, source `ipfstat.c`, and manual `ipfstat.8`.
- Links with `tinfow` and `ncursesw`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
The curses libraries support interactive/stat display modes in `ipfstat`.

## Risk Notes
Build depends on wide-character curses and terminfo libraries being available in the target build environment.
