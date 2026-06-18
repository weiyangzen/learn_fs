# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fgetattr.rs

## Purpose
This module defines the `fgetattr` performance counter suite for reading attributes through an open file handle. It measures root, nested, and deeply nested files, both leaving the handle open and releasing it after the attribute read.

## Important APIs, Types, And Functions
The registered cases are `file_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir`, each instantiated with `CLOSE_AFTER=false` and `true`. The operation under test is `filesystem.fgetattr(file_ino.clone(), &file_fh)`. The optional close path uses `maybe_close`.

The module depends on `FilesystemDriver`, `ActionCounts`, `FixtureType`, `TestDriver`, `TestReady`, `BlobStoreActionCounts`, `HLActionCounts`, `LLActionCounts`, `AbsolutePath`, and `PathComponent`.

## Control Flow
Each setup creates and opens a file. The test phase reads attributes from the open file handle and optionally releases the handle. Expected counts compute `close_after` and branch by fixture type. Unlike mutation tests, no `blob_data_mut` is expected for the read itself.

## State And Persistence Behavior
`fgetattr` is read-only, but optional release can flush the file handle. Expected `blob_flush` and high-level `store_flush_block` equal `close_after`, while low-level stores remain absent. The operation loads metadata and reads blob data; no-cache fuser costs grow with path depth.

## Dependencies And Integration Points
This file exercises the open-handle attribute API rather than path-based `getattr`. It integrates with the same generated test matrix as write-like handle operations and with shared close behavior.

## Risks And Edge Cases
The suite does not verify returned attribute contents, only counters and success. It does not cover closed/invalid handles, directories, symlinks, root attributes, or atime-specific expectation differences even though the macro runs all atime modes. TODOs question expected counter values.

## Test Signals
Key signals are absence of mutation counters during `fgetattr`, presence of release flush counters when `CLOSE_AFTER=true`, and fixture/path-depth differences in loads and reads. This should catch accidental writes or cache regressions in attribute lookup.
