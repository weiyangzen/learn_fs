# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_util.c

## Purpose
Filename character, comparison, and translation utilities for ISO 9660, Joliet, and optional iconv conversion.

## Main Elements
- `isochar()` reads one ISO/Joliet character, using iconv when enabled or simple UCS-2 fallback for Joliet.
- `isofncmp()` compares a user pathname component with an ISO filename, case-folding plain ISO uppercase and allowing omitted `;version` suffixes.
- `isofntrans()` translates ISO directory names into visible names, optionally preserving original case/version and adding the associated-file prefix.
- `sgetrune()` obtains one local filename rune, using iconv when enabled or one-byte fallback otherwise.

## Dependencies And Integration
Used by lookup, readdir, and Rock Ridge default-name logic; depends on cd9660 mount flags and iconv handles.

## Risk Notes
Name comparison and translation differ by Joliet/iconv flags, so mount options affect path lookup semantics.
