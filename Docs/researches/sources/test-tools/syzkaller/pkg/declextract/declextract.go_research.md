# sources/test-tools/syzkaller/pkg/declextract/declextract.go

Purpose: `declextract.go` is the main orchestration and type-lowering logic for converting clang extraction output into syzkaller description text plus interface metadata. `Run` builds a mutable `context`, processes functions, typing facts, constants, enums, structs, syscalls, io_uring operations, serializes generated descriptions, finalizes interfaces, and returns `Result`.

Important APIs/types/functions: `Result` exposes `Descriptions`, discovered `Interfaces`, constant-to-include usage, and `StructInfo`. `context` carries input `Output`, iface probe coverage, syscall rename rules, lookup maps, generated includes/defines/interfaces, and accumulated errors. `processConsts`, `processEnums`, `processSyscalls`, `emitSyscall`, `processIouring`, `processStructs`, `processFields`, and the `fieldType*` family are the major passes.

Control flow and state: most work mutates the shared context. Constants are split into kernel header includes versus explicit `define` records, then sorted and deduplicated. Structs and enums get the `$auto` suffix before references are serialized. Syscalls are duplicated into command-specific variants when dataflow discovers switched command arguments; ordinary variants are then refined by inferred argument and return types.

Dependencies and integration: this file depends on `clangtool.SortAndDedupSlice`, coverage data, ifaceprobe file coverage, and helper passes in `typing.go`, `interface.go`, `fileops.go`, `netlink.go`, and `serialization.go`. It emits syzkaller DSL constructs such as `ptr`, `array`, `flags`, `len`, `filename`, `sockaddr`, and generated resources.

Risks: heuristics are deliberately broad. Name-based fd/path/network recognition may misclassify fields; recursive pointer handling uses parent-name and `next` heuristics; unsupported bitfields, bounds, and missing structs become accumulated errors or panics. There are no direct tests in this subset, so confidence comes from integration with generated descriptions and downstream syzlang parsing.
