# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPrint.cc

## Purpose
Implements the `pfc_print` utility for inspecting `.cinfo` metadata files or recursively walking cache directories and printing metadata in human-readable or JSON form.

## Important APIs, Types, and Functions
- `Print::Print()` configures units/format and dispatches to file or directory printing.
- `isInfoFile()` identifies `.cinfo` suffixes.
- `printFileJson()` reads `Info` metadata and emits JSON with version, creation time, checksum state, file/block sizes, completion state, optional block array, no-checksum time, and access records.
- `printFile()` emits equivalent text tables.
- `printDir()` recursively traverses directories and prints `.cinfo` files.
- `main()` parses CLI options, loads OSS configuration through `XrdOfsConfigPI`, supports `root:/` path mapping via `oss.localroot`, and instantiates `Print` for each path.

## Control Flow
CLI parsing validates units and flags, optionally attaches a config file, suppresses OSS init logs, loads the OSS plugin, then processes each path. A path ending in `.cinfo` is opened as metadata; otherwise the utility opens a directory and recursively prints metadata files below it.

## State and Persistence Behavior
The utility is read-only from the cache metadata perspective. It opens `.cinfo` files read-only and creates temporary `Info` objects. Output goes to stdout. It does not mutate access times except through underlying filesystem read semantics.

## Dependencies and Integration Points
Depends on `Info`, `XrdOucStream`, `XrdOucArgs`, `nlohmann::json` via `XrdOucJson`, `XrdOfsConfigPI`, `XrdSysLogger`, and `XrdOss`. It is operational tooling for administrators and tests.

## Risks and Test Signals
Risks include `isInfoFile()` indexing before the start for paths shorter than six characters, not checking all open failures before `Info::Read`, recursive directory loops if OSS exposes unusual entries, and JSON percentage division by zero for zero-block files. Tests should cover CLI validation, short paths, unreadable `.cinfo`, verbose block output, JSON schema, and config-based `root:/` mapping.
