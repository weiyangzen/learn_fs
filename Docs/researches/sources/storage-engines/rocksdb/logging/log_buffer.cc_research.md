# sources/storage-engines/rocksdb/logging/log_buffer.cc

Purpose: Implementation of deferred info-log buffering for code paths that cannot log immediately, often while holding mutexes.

Important APIs/types/functions: `LogBuffer::AddLogToBuffer`, `FlushBufferToLog`, free functions `LogToBuffer`.

Control flow and state: `AddLogToBuffer` skips messages below the logger’s current level, allocates a fixed-size record from an `Arena`, stores current time, formats the message with truncation, NUL-terminates it, and appends the record pointer. `FlushBufferToLog` iterates buffered records, formats original timestamp metadata, logs each message at the buffer’s level, and clears the vector.

State and persistence behavior: messages live in the buffer’s arena until the buffer is destroyed; flushing writes them to the target logger. Clearing drops pointers but arena memory remains allocated for the buffer lifetime.

Dependencies and integration points: `Arena`, `autovector`, port time functions, generic `Log`.

Risks: max log size truncates messages; arena memory is not reclaimed on flush. If local time conversion fails, a buffered entry is skipped. Thread safety is not provided.

Test signals: indirectly covered through event logging and subsystems using buffered logs; no dedicated test in this subset.
