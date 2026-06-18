# File Research: sources/os/plan9/9front/sys/src/cmd/scat/strings.c

Purpose: Static name tables for `scat`.

Content:
- `greek`: 1-indexed Greek-letter names.
- `greeklet`: corresponding Unicode rune values.
- `constel`: 1-indexed constellation abbreviations.
- `names`: accepted object-type aliases mapped to `sky.h` type enum values.

Integration: Included directly by `scat.c`, and used by name parsing, display labels, command parsing, and record filtering.

Risks:
- Index values are semantically significant, especially star-name encoding and constellation IDs.
