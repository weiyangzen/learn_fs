# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucExport.cc

## Purpose
Implements parsing for export path options in XRootD/OSS configuration.

## Important APIs, Types, And Functions
`ParseDefs` consumes option words from `XrdOucStream` and mutates a 64-bit flag set using a static table mapping names such as `readonly`, `forcero`, `cache`, `mig`, `mkeep`, `mlock`, `mmap`, `stage+`, `nodread`, `local`, `globalro`, `noxattrs`, and `noficl`. Each entry defines bits to remove, bits to add, and mask bits marking options explicitly set. `ParsePath` parses the path, applies defaults, validates conflicts, and inserts/updates an `XrdOucPList` in an `XrdOucPListAnchor`.

## Control Flow
`ParseDefs` loops over remaining config words and logs warnings for unknown options. `ParsePath` obtains the path, handles object-id wildcard paths beginning with `*`, merges defaults for unspecified options using the high mask half, forces readonly semantics for memory mapping on writable paths, rejects `noxattrs` combined with migration/purge, and either updates an existing matching path or inserts a new node.

## State And Persistence
No static mutable state. Persistent runtime state is the caller-owned export prefix list and per-node flag values. Config parsing changes in-memory namespace policy.

## Dependencies And Integration Points
Depends on `XrdOucExport.hh`, `XrdOucPList`, `XrdOucStream`, `XrdSysError`, and platform `strlcpy`. It integrates with OSS namespace export directives and downstream access, staging, migration, and cache policy checks.

## Risks And Test Signals
Risks include subtle default-mask logic, warnings rather than hard failures for unknown options, path truncation at 1024 bytes, and conflicts that are only partially validated. Test signals include parsing every option pair, default inheritance, repeated path update semantics, wildcard path behavior, memory-map forcing, and `noxattrs` conflict rejection.
