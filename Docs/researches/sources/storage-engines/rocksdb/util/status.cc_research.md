# sources/storage-engines/rocksdb/util/status.cc

## Purpose

Implements heap-backed status message copying, status construction with optional secondary messages, message appending, and human-readable `Status::ToString`.

## APIs, control flow, and state

`Status::CopyState` duplicates a C string into `unique_ptr<const char[]>`. The main constructor combines `msg` and optional `msg2` with `": "` into a null-terminated state buffer while storing code, subcode, severity, retry flags, and scope. `CopyAppendMessage` creates a new status preserving code/subcode/severity and appending a delimiter/message to existing state. `ToString` maps status codes to prefixes, maps subcodes through a static message table, and appends state text.

## Dependencies and integration

It depends on `rocksdb/status.h`, C string functions, and platform headers. Every RocksDB subsystem relies on these formatting and copying semantics for surfaced errors.

## Risks and test signals

Risks are enum/table drift for `Status::SubCode`, null state handling, and losing severity/subcode during append. `slice_test.cc` includes `StatusTest.Update`, but this subset does not directly assert every `ToString` mapping. Assertions guard `kMaxSubCode` and unexpected `kMaxCode`.
