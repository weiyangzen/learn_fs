# sources/test-tools/crashmonkey/ace/common.py

## Purpose

`common.py` centralizes the small filesystem namespace and operation-domain constants used by the Python 3 ACE generator. It provides the legal parameter values for filesystem operations and the canonical mapping from J-lang logical file names to shell/path names and parent/type metadata.

## Important APIs, Types, and Values

The module exports lists rather than functions or classes. `FallocOptions` enumerates Linux fallocate modes used by generated workloads, including zero-range, zero-range keep-size, punch-hole keep-size, keep-size, and `0`. `FsyncOptions` contains `fsync`, `fdatasync`, and `sync`.

`FileOptions`, `SecondFileOptions`, `DirOptions`, `TestDirOptions`, and `SecondDirOptions` define the default small namespace. The default file set uses `foo` and `A/foo` as first-file options, `bar` and `A/bar` as second-file options, `A` and `B` as subdirectories, and `test` as the root mount/test directory. The split between first and second file options is used by generators to reduce symmetric duplicate workloads.

`WriteOptions`, `dWriteOptions`, and `TruncateOptions` define logical write shapes. Normal writes can append, overlap with an unaligned start, or overlap and extend. Direct writes can append or overlap at the start. Truncates can be aligned or unaligned.

`OperationSet` is the default core-operation set for `ace.py`: `creat`, `mkdir`, `falloc`, `write`, `dwrite`, `mmapwrite`, `link`, `unlink`, `remove`, `rename`, `fsetxattr`, `removexattr`, and `truncate`.

`JLANG_FILES` maps J-lang logical names to bash/runtime paths, parent logical names, and coarse file type. It includes root/test entries, `A`, nested `AC` as `A/C`, `B`, base files `foo` and `bar`, directory-scoped files such as `Afoo` and `Bbar`, and nested files such as `ACfoo`.

## Control Flow

There is no runtime control flow in this module. It is imported by `ace.py`, and the imported lists are consumed by `buildTuple()`, dependency checks, parent/sibling logic, and J-lang emission. Some values are mutated by `ace.py` at runtime for demo and nested modes, so these constants act as process-local defaults rather than immutable configuration.

## State and Persistence Behavior

All state is module-level in-memory Python list data. There is no file I/O, no persistence, and no initialization function. Because importers may mutate these lists directly, repeated generator invocations in the same Python process can observe prior modifications unless the interpreter is restarted or the lists are copied defensively.

## Dependencies and Integration Points

The module has no imports. Its main integration points are `ace.py` and any other generator that wants to share the Python 3 operation domains. `JLANG_FILES` documents an intended bridge between arbitrary J-lang names and actual filesystem paths, although `ace.py` also contains separate hard-coded `Parent()` and `SiblingOf()` logic that must remain consistent with these constants.

## Risks and Test Signals

The largest risk is domain drift. `common.py`, `ace.py`, and the older sequence generator scripts duplicate overlapping operation and namespace definitions. If one list gains a new logical path or operation without matching updates to `Parent()`, `SiblingOf()`, `buildJlang()`, and adapter support, generated workloads can become invalid or silently omit cases.

The `JLANG_FILES` entry for `"test"` has type `"file"` even though comments and generator logic treat `test` as the root directory. If code begins relying on this type field, that mismatch may matter. `FallocOptions` mixes strings and integer `0`, which `buildJlang()` stringifies correctly today but can surprise callers that expect uniform strings.

Good tests are small consistency checks: every file option should have a parent mapping, every sibling should exist in one of the option sets, every operation in `OperationSet` should be supported by `ace.py` and `cmAdapter.py`, and every `JLANG_FILES` logical name should map without collisions after slash removal.
