# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_util.c

## Scope

Provides ISO/Joliet filename character extraction, name comparison, name translation, and local-rune extraction helpers.

## APIs And Behavior

- `isochar()` decodes one ISO filename character. Plain ISO consumes one byte; Joliet consumes two bytes and optionally runs through kernel iconv.
- `isofncmp()` compares a user/local filename against an ISO filename, allowing omitted `;version` suffixes and case-insensitive matching for uppercase ISO names.
- `isofntrans()` translates ISO directory-entry names into visible directory-entry names, optionally lowercasing non-original ISO names, stripping generation suffixes, and prefixing associated files with `=`.
- `sgetrune()` extracts one local character, using iconv when `ISOFSMNT_KICONV` is active.

## Dependencies

Uses CD9660 mount flags and iconv state, `cd9660_iconv`, Joliet level from the mount, and ISO name constants from `iso.h`.

## Risks And Invariants

Joliet decoding depends on two-byte units and can degrade to `?` without iconv. Version stripping and case folding are part of lookup semantics, so mismatches here affect name resolution and directory output consistency.
