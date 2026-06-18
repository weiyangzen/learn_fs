# sources/test-tools/syzkaller/prog/decodeexec.go

Purpose: decodes the irreversible executor binary format into inspectable `ExecProg` structures for tests, diagnostics, and size accounting.

Important APIs/types/functions: `ExecProg`, `ExecCall`, `ExecCopyin`, `ExecCopyout`, `ExecArgConst`, `ExecArgResult`, `ExecArgData`, `ExecArgCsum`, `ExecCsumChunk`, `ExecCallCount`, `Target.DeserializeExec`, and `execDecoder` methods `parse`, `readCallProps`, `readArg`, `read`, `readBlob`, `commitCall`, `addStat`.

Control flow and state: parsing reads varints from `data`, beginning with call count, then processes copyin/copyout/set-props/syscall/EOF instructions. `commitCall` finalizes pending calls before instruction boundaries, updates `numVars`, and resets decoder call state. Result args extend `vars` with default values. Stats are accumulated hierarchically by slash-separated path prefixes.

Dependencies and integration: mirrors constants and wire layout from `encodingexec.go`, adds `target.DataOffset` back to physical addresses, and uses target syscall tables to resolve call IDs.

Risks: decoder must stay byte-for-byte compatible with serializer changes. It rejects bad syscall IDs, unsupported checksum kinds, bad top-level arg kinds, varint/blob overflow, and mismatched call counts. It decodes for inspection, not for reconstructing a normal `Prog`.

Test signals: `encodingexec_test.go` round-trips serialized executor buffers through `DeserializeExec`, compares selected decoded structs, validates `ExecCallCount`, and records stats in random tests.
