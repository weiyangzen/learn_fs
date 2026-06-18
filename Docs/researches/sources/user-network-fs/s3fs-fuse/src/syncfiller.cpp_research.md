# sources/user-network-fs/s3fs-fuse/src/syncfiller.cpp

## Purpose
Implements `SyncFiller`, a small synchronization wrapper around FUSE `fuse_fill_dir_t` callbacks. It serializes concurrent directory-entry filling and suppresses duplicate names while s3fs builds `readdir` responses from multiple sources.

## Important APIs, Types, And Control Flow
The constructor stores the FUSE buffer and callback and aborts on null inputs. `Fill(name, stbuf, off)` locks the mutex, inserts `name` into the `filled` set, and calls `filler_func` only for the first occurrence. `SufficiencyFill(pathlist)` locks once, iterates a vector of names, fills missing entries with null stat and offset zero, and returns `1` if any callback invocation fails.

## State And Persistence
State is in-memory per `SyncFiller`: the FUSE buffer pointer, callback pointer, mutex, and `std::set<std::string>` of names already returned. It performs no persistence; output is written into the caller-owned FUSE readdir buffer.

## Dependencies And Integration Points
Depends on `s3fs_logger.h` and `syncfiller.h`, which pulls in FUSE types through `s3fs.h`. It integrates with directory listing code where object-derived, implicit, and sufficiency entries can arrive concurrently or with overlap.

## Risks And Test Signals
The constructor aborts rather than returning an error, so caller validation matters. Holding the lock while invoking the FUSE filler callback can serialize long callbacks and could deadlock if the callback re-enters the same `SyncFiller`. Duplicate suppression is by exact string only. Integration test list, implicit directory, non-existing directory object, and duplicate/missing readdir cases provide indirect signals.
