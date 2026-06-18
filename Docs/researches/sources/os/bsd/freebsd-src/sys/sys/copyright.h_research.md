# File Research: sources/os/bsd/freebsd-src/sys/sys/copyright.h

## Purpose
Defines compiled-in FreeBSD copyright and trademark strings.

## Main Elements
- `COPYRIGHT_Vendor` can be supplied externally or defaults to empty.
- `COPYRIGHT_FreeBSD`, `TRADEMARK_Foundation`, and `COPYRIGHT_UCB` string macros.
- Defines global `copyright[]` and `trademark[]`.

## Dependencies And Integration
Used by kernel/userland components that embed or print system copyright and trademark text.

## Risk Notes
This header defines objects, not just declarations. Including it in multiple compilation units would create duplicate definitions unless the build expects that pattern.
