# sources/storage-engines/sqlite/tool/sqlite3_rsync.c

## Purpose
`sqlite3_rsync.c` is a standalone SQLite utility that copies a live SQLite database from an origin to a replica using a custom rsync-like protocol. It minimizes bandwidth by comparing page hashes, then sending only pages that differ. It supports local-to-remote, remote-to-local, and local-to-local operation, with SSH used for remote execution of the same binary in `--origin` or `--replica` mode.

## Important APIs, types, and functions
The central state carrier is `SQLiteRsync`, which stores origin/replica paths, streams, debug/error files, the SQLite connection, verbosity, protocol version, WAL-only policy, byte counters, page metadata, and hash/page statistics. Protocol constants define origin messages (`ORIGIN_BEGIN`, `ORIGIN_DETAIL`, `ORIGIN_PAGE`, `ORIGIN_TXN`, `ORIGIN_END`, etc.) and replica messages (`REPLICA_HASH`, `REPLICA_CONFIG`, `REPLICA_READY`, etc.).

Process integration is handled by `popen2()`/`pclose2()`, with Unix pipe/fork/exec support and a Windows `CreateProcessW` implementation. `append_escaped_arg()` and `add_path_argument()` build shell-safe SSH commands, including a retry path for remote shells with limited `PATH`.

The file embeds a reduced-round Keccak hash engine exposed to SQLite as `hash(X)` and `agghash(X)` through `hashRegister()`. SQL helpers (`prepareStmt()`, `runSql()`, `runSqlReturnUInt()`, `runSqlReturnText()`) centralize statement preparation and error reporting. Wire helpers (`readUint32()`, `writeUint32()`, `readByte()`, `writeByte()`, `readBytes()`, `writeBytes()`, `readPow2()`, `writePow2()`) implement the binary protocol. The core protocols are `originSide()` and `replicaSide()`, while `sendHashMessages()` and `subdivideHashRange()` drive hash batching.

## Control flow
`main()` parses options, determines which of `ORIGIN` or `REPLICA` is remote using `hostSeparator()`, launches the remote side with SSH or a local child process, then runs either `originSide()` or `replicaSide()` locally. Direct `--origin` and `--replica` modes run over stdin/stdout for remote invocation.

On the origin side, the tool opens the origin database read/write, starts a transaction, registers hash functions, reads `page_count` and `page_size`, sends `ORIGIN_BEGIN`, then receives replica hashes. Mismatched hashes are stored in a temp `badHash` table. For protocol v2, multi-page hash mismatches produce `ORIGIN_DETAIL` requests so the replica can subdivide ranges. Once detail is sufficient, the origin reads changed pages from `sqlite_dbpage('main')`, skips the lock-byte page, sends `ORIGIN_PAGE` records, then sends `ORIGIN_TXN` and `ORIGIN_END`.

On the replica side, `ORIGIN_BEGIN` causes an in-memory SQLite database to attach the replica file as schema `replica`. It creates a `sendHash` table, checks page size and WAL policy, builds initial hash ranges, and sends hashes. When pages arrive, it writes them through `sqlite_dbpage(pgno,data,schema)`. At `ORIGIN_TXN`, it truncates if needed by inserting `NULL` at page `nOPage+1`, then commits.

## State and persistence behavior
Persistent state is the replica database file and possibly its WAL/journal files. The origin runs inside a read transaction to observe a stable snapshot. The replica uses `BEGIN IMMEDIATE` and writes raw database pages with `PRAGMA writable_schema=ON` and `sqlite_dbpage`; this is intentionally low-level and bypasses normal table-level SQL semantics. Debug/error/log files are appended or written when configured. Counters in `SQLiteRsync` are runtime-only.

If the replica started in WAL mode, page 1 header bytes are adjusted to avoid switching it out of WAL mode. `--wal-only` rejects synchronization when the origin or existing replica is not WAL. The protocol may retry remote command startup with a `PATH=...` prefix if the first SSH invocation yields no hashes.

## Dependencies and integration points
The utility depends on SQLite core APIs, the `sqlite_dbpage` virtual table, SQLite string builders, SQLite VFS time, the `sha1` extension initializer declaration, standard C/POSIX or Win32 process APIs, and SSH for remote operation. It integrates with SQLite build tooling as a command-line binary and with remote systems by invoking the same binary with `--origin`/`--replica`.

## Risks and edge cases
The protocol is binary and stateful; any desynchronization can produce confusing message errors. It relies on raw page writes, so page size mismatches, encoding attach failures, WAL mode transitions, interrupted writes, or missing `sqlite_dbpage` support are high-risk. The reduced-round hash is for change detection, not cryptographic authentication. Command construction is careful, but remote path parsing still treats `HOST:PATH` syntax specially and can be ambiguous with unusual filenames. `pclose2()` waits for any child with `waitpid(0,...)`, which is acceptable for this utility but broad. Error handling counts write failures separately and loops while `nErr <= nWrErr`, so communication failures are central to correctness.

## Test signals
Useful test signals include `--commcheck`, `--arg-escape-check`, protocol downgrade via `--protocol`, `--wal-only` rejection cases, verbose counters (`hashes`, rounds, page updates), local-to-local sync, remote-origin and remote-replica modes, page-size mismatch tests, and database content verification after sync. Debug logs from `--debugfile` expose exact message flow.
