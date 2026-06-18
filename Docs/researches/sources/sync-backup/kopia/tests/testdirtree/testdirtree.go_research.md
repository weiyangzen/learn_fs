<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testdirtree/testdirtree.go -->
# sources/sync-backup/kopia/tests/testdirtree/testdirtree.go

This file provides utilities for creating randomized directory trees for tests. It supports random hex or Unicode names, nested directories, random file contents, symlinks, configurable depth/count/size/name options, and counters for created objects and bytes.

Important APIs are `DirectoryTreeOptions`, `MaybeSimplifyFilesystem`, `DirectoryTreeCounters`, `MustCreateDirectoryTree`, `CreateDirectoryTree`, `MustCreateRandomFile`, and `CreateRandomFile`. Control flow recursively creates directories, then random files, then symlinks. File contents are generated from a `math/rand` source seeded with `clock.Now`.

State is filesystem output plus an atomic global name counter for uniqueness. Dependencies are Unicode normalization, platform complexity helpers, and test utilities. Risks include nondeterminism, symlink behavior on restricted platforms, ARM complexity reduction containing a likely assignment typo for `MaxSubdirsPerDirectory`, and cryptographic random errors ignored in name generation. Tests using this helper validate snapshot/restore edge cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testdirtree/testdirtree.go -->
