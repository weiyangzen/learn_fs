# sources/test-tools/syzkaller/prog/encodingexec.go

Purpose: serializes `Prog` into the compact executor binary instruction stream.

Important APIs/types/functions: executor op/arg constants, `ExecBufferSize`, `ExecNoCopyout`, `execMaxCommands`, `Prog.SerializeForExec`, `execContext.serializeCall`, `serializeKFuzzTestCall`, `writeCallProps`, `writeCopyin`, `willBeUsed`, `writeChecksums`, `writeCopyout`, `writeArg`, and `writeConstArg`.

Control flow and state: `SerializeForExec` validates, writes call count, serializes each call with fresh per-call checksum maps, writes EOF, and enforces buffer/copyout limits. Normal calls emit copyins, checksum copyins in reverse address order, call props, syscall instruction, result copyout ID if needed, top-level args, then post-call copyouts. `execContext` persists the byte buffer, arg address/copyout map, and global copyout sequence. KFuzzTest calls write the test-name copyin, marshal the struct argument into a relocation blob, copy it into a provided buffer, update the length arg, and defer final syscall emission.

Dependencies and integration: relies on `calcChecksumsCall`, `ForeachArg`, target physical addresses/data offset, `CallProps.ForeachProp`, `MarshallKFuzztestArg`, binary varint encoding, and arg/resource metadata.

Risks: this is an executor ABI; opcode/meta changes must stay synchronized with executor and `decodeexec.go`. Mutating the KFuzzTest length arg during serialization is observable if the caller reuses the program. Error from `serializeCall` is currently ignored in the main loop except for later size limits, preserving existing dashboard behavior. Incorrect `willBeUsed` bookkeeping causes missing copyouts or checksum data.

Test signals: `encodingexec_test.go` checks exact instruction streams for alignment, unions, arrays, endian formats, bitfields, resources, checksums, call props, copyout vars, random decodeability, and overflow errors.
