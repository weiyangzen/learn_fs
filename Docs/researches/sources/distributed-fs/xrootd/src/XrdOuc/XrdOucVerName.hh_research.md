<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.hh

## Purpose

`XrdOucVerName.hh` declares a small static helper class for applying and detecting XRootD plugin shared-library version suffixes.

## Important APIs, Types, And Functions

- `hasVersion(const char *piPath, char **piNoVN = 0)` returns an embedded numeric version and optionally an allocated unversioned fallback.
- `Version(const char *piVers, const char *piPath, bool &noFBK, char *buff, int blen)` writes a versioned path into caller storage and reports fallback policy.
- Private `isOurs()` checks whether a basename belongs to the official strict-name table.

## Control Flow

Consumers typically call `Version()` when resolving configured plugin paths against the running XRootD plugin version, and `hasVersion()` to warn or adjust behavior when a user supplied an already-versioned library.

## State And Persistence

The class has no instance state and is not meant to be instantiated. Memory returned through `piNoVN` is heap allocated by the implementation.

## Dependencies And Integration Points

The header is intentionally minimal and avoids pulling in plugin loader headers. It is integrated by shared library loading paths that need versioned module names.

## Risks And Edge Cases

- The API uses raw `char*` ownership and caller-managed buffers.
- `noFBK` is an output policy flag whose meaning is easy to miss: strict official names must load the exact versioned path.
- Documentation contains minor typos, so tests and call-site behavior are the reliable contract.

## Test Signals

Compile tests should confirm the header is standalone. Behavior tests should pair the declarations with implementation cases for official names, third-party names, already-versioned names, and buffer-too-small outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.hh -->
