## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TraceFileIO.h

Purpose: Declares debug hooks that track file contents in memory and validate reads/writes/truncates against expected data.

Important APIs/types/functions: `debugFileCheck(context, file, data, offset, length)` validates a block against tracked state. `debugFileSet(context, file, data, offset, length)` updates tracked bytes. `debugFileTruncate(context, file, offset)` invalidates tracked data after a truncate point.

Control flow: Implementations are elsewhere. File IO paths call set/truncate as writes occur and check when reads or validation points occur, including a context string for trace/debug identification.

State and persistence behavior: The tracked file data is in-memory debug state outside this header. It mirrors durable file mutations for validation but is not the real durable store.

Dependencies and integration points: Depends on Flow base types. Integrated with debug/simulation file IO validation paths.

Risks: If file IO paths miss a set/truncate call, later checks can produce false positives. Large tracked files can consume memory depending on implementation. It should remain debug-only or carefully gated in production.

Test signals: Write/read validation, truncate invalidation, offset/length edge cases, context/file separation, and simulation corruption detection.
