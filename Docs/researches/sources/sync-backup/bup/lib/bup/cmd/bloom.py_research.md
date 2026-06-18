# sources/sync-backup/bup/lib/bup/cmd/bloom.py

## Purpose
Command implementation for `bup bloom`, supporting creation/update, validation against idx/midx files, forced regeneration, output/dir selection, hash count selection, and deliberate bloom ruin for tests.

## Important APIs, Types, and Functions
Defines `optspec`, `ruin_bloom`, `check_bloom`, `do_bloom`, and `main`. Uses `BloomReader`, `BloomWriter`, `BloomInvalid`, `BloomNotFound`, `git.open_idx`, `git.open_object_idx`, and `git.repo`.

## Control Flow
`main` parses options, resolves the pack directory and output path, dispatches check/ruin/build. `do_bloom` reads existing bloom when allowed, counts idx files into add/rest sets, decides whether to append or regenerate based on entry count/k/false-positive threshold, adds idx shatables, and renames temp bloom into place.

## State and Persistence Behavior
Reads `.idx`/`.midx` files and writes/updates `bup.bloom` or requested output. `ruin` zeroes the bitfield while preserving file structure.

## Dependencies and Integration Points
Command layer over `bup.bloom` and Git pack indexes. Integrates with repository discovery, progress/logging, saved error status, and object index formats.

## Risks and Test Signals
Risks include stale idx name lists, false-positive threshold decisions, division by zero when add_count is zero avoided by early return, and temporary bloom cleanup. Signals are successful check membership, invalid/missing bloom errors, force regeneration, and correct exit codes.
