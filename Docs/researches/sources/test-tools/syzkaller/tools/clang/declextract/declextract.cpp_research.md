<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/declextract.cpp -->
# sources/test-tools/syzkaller/tools/clang/declextract/declextract.cpp

## Purpose

Clang LibTooling declaration extractor for syzkaller description generation.

## Important APIs, Types, and Functions

Class `Extractor`, matcher thunk, `PPCallbacksTracker`, `ConstDesc`, `FunctionAnalyzer`; helpers `genType`, `extractRecord`, `extractEnum`, `extractIoctl`, `evaluate`, `findAllMatches`, `getTypingEntity`.

## Control Flow

When `SYZ_RUN_CLANGTOOL=declextract`, runs matchers for function definitions, `SYSCALL_DEFINEx`, io_uring tables, `nla_policy`, generic netlink families, and `file_operations`, emitting type/const/function/syscall/ioctl/netlink/file-op JSON plus typing facts from function bodies.

## State and Persistence Behavior

Maintains macro map, dedup maps, current matcher bindings, AST/source managers, and `Output`; persists only stdout JSON.

## Dependencies and Integration Points

Depends on Clang AST matchers/tooling, Linux ioctl macros, kernel compilation databases, and local JSON/output schema; feeds Go syzlang tooling.

## Risks and Edge Cases

Best-effort inference: other-TU definitions become TODO, anonymous names are heuristic, nested anonymous aggregate indexing is incomplete, indirect calls are ignored, non-int constants evaluate to zero.

## Test Signals

Golden tests over declextract testdata and kernel snippets for structs, bitfields, counted arrays, ioctls, netlink, io_uring, and file ops.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/declextract.cpp -->
