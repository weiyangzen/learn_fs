# sources/sync-backup/bup/lib/bup/cmd/drecurse.py

## Purpose
`cmd/drecurse.py` exposes the filesystem traversal engine as a CLI. It prints, profiles, or silently consumes the recursive directory listing used by indexing and backup flows.

## APIs and Control Flow
`main(argv)` requires exactly one path, parses literal and regex excludes, normalizes literal excludes relative to a relative traversal root, and calls `bup.drecurse.recursive_dirlist`. With `--profile` it consumes under `cProfile`; with `--quiet` it drains without output; otherwise it writes each path as bytes to stdout.

## State, Dependencies, Integration, Risks, Tests
The command does not persist state. It depends on `bup.drecurse`, exclude parsers, `argv_bytes`, and `byte_stream`. It is a direct diagnostic surface for the traversal behavior that `bup index` relies on. Risks center on path normalization differences between absolute and relative roots, regex/literal exclude parity with `index`, and traversal errors being reported through shared helper error state. Test signals include one-file-system behavior, exclude matching, profile/quiet modes, byte path output, and exact one-argument validation.
