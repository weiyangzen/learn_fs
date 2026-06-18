<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.cc

## Purpose

`XrdOucVerName.cc` implements shared-library plugin name versioning. It detects already-versioned plugin paths, recognizes official strict plugin names, and constructs versioned library filenames such as `libXrdFoo-5.so`.

## Important APIs, Types, And Functions

- Anonymous `StrictName[]` is initialized from `XrdVERSIONPLUGINSTRICT` and lists official plugin filenames that require strict version handling.
- `XrdOucVerName::hasVersion()` detects a trailing `-<number>.so` component and optionally returns an unversioned fallback path for official plugin names.
- `XrdOucVerName::isOurs()` strips directory prefixes and tests membership in `StrictName`.
- `XrdOucVerName::Version()` inserts `-<version>` before the filename extension and reports whether fallback is disallowed.

## Control Flow

`hasVersion()` searches the full path for the last dash, parses the following decimal value, and accepts it only when the remaining suffix is `.so`. If a caller asks for an unversioned fallback, it reconstructs the path without the numeric suffix and returns it only when that unversioned name is in the strict official-name table.

`Version()` splits the path into directory, basename, and extension, checks strict-name membership by basename, sets `noFBK`, and formats the versioned result into the supplied buffer.

## State And Persistence

The file has no mutable state and no persistent I/O. It may allocate an alternate path through `strdup()` in `hasVersion()`; the caller owns that memory.

## Dependencies And Integration Points

It depends on `XrdVersionPlugin.hh` for `XrdVERSIONPLUGINSTRICT` and on `XrdOucVerName.hh` for declarations. It integrates with plugin loaders that need ABI-versioned module lookup and fallback behavior.

## Risks And Edge Cases

- Version detection only accepts `.so`, so platform-specific shared-library suffixes are outside this implementation.
- `hasVersion()` uses a fixed 2048-byte stack buffer for fallback construction.
- `Version()` calls `snprintf(buff, blen-1, ...)`, which leaves one byte unused and can behave badly for very small `blen`.
- Only official strict names get unversioned fallback handling; third-party versioned libraries return no alternate path.

## Test Signals

Tests should cover strict official names, non-strict third-party names, paths with multiple dashes, no-extension names, insufficient output buffers, already-versioned `.so` paths, and ownership/freeing of `piNoVN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.cc -->
