# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/intermediate_types.go

## Purpose
This file defines the intermediate representation used by `syz-trace2syz` while converting parsed strace lines into syzkaller programs.

## Important APIs, types, and functions
- `TraceTree` stores per-PID traces, parent-child relationships, and root PID; `NewTraceTree` initializes maps; `add` inserts calls and records clone children.
- `Trace` is an ordered syscall list; `Trace.add` appends normal calls or merges resumed calls into the last paused call.
- `IrType` is the interface implemented by parsed argument types.
- `Syscall` stores call name, args, PID, return value, and paused/resumed flags; `NewSyscall` and `String` construct/display it.
- `GroupType`, `Constant`, and `BufferType` model aggregate arguments, evaluated numeric constants, and string/identifier buffers.

## Control flow
`TraceTree.add` sets the first seen PID as root, creates a trace lazily, delegates insertion to `Trace.add`, and records `clone` return values as children when the call is not paused. `Trace.add` merges resumed syscall fragments by appending args, clearing paused, and replacing return value on the last call.

## State and persistence behavior
All state is in-memory parser IR. There is no file or external state. The parent tree and traces persist only for downstream trace-to-program generation.

## Dependencies and integration points
Used by parser grammar actions in `strace.y`/`strace.go`, line parsing in `parser.go`, and prog generation packages. `Constant.Val` and `BufferType.Val` are consumed by call selection and argument generation.

## Risks and edge cases
`Trace.add` assumes a resumed fragment always follows an existing paused call for that PID; malformed traces can panic on an empty call list. Clone child detection assumes clone return value is the child PID and does not filter failed clone returns. Root PID is first parsed PID, not necessarily process-tree root in arbitrary trace ordering.

## Test signals
`parser_test.go` covers root PID, clone tree creation, resumed calls, expression constants, and group types, giving direct coverage of these IR operations.
