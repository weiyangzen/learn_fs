# sources/storage-engines/rocksdb/tools/ldb_test.py

## Purpose
This Python unittest module exercises the built `./ldb` executable as an end-user CLI. It validates simple put/get/delete flows, batch and entity writes, blob DB flags, scans, dump/load, hex and TTL modes, transaction DB opening, administrative commands, live-file dumps, manifest/WAL/SST/blob dumps, properties, column families, and external SST ingestion.

## Important APIs, Types, and Functions
`my_check_output()` is a compatibility wrapper around `subprocess.Popen` that raises on nonzero exit. `run_err_null()` shells a command while suppressing stderr. `LDBTestCase` owns a per-test temporary directory, `dbParam()`, `assertRunOKFull()`, `assertRunFAILFull()`, convenience wrappers for default DB calls, and helpers such as `dumpDb`, `loadDb`, `writeExternSst`, `ingestExternSst`, `dumpLiveFiles`, `listLiveFilesMetadata`, and file globbers for MANIFEST/SST/WAL/blob files.

## Control Flow
Each test creates an isolated temp directory in `setUp()` and removes it in `tearDown()`. Assertions run shell commands against `./ldb`, often filtering background-thread creation messages. Tests build data with `put`, `batchput`, `put_entity`, or blob-enabled writes, then validate command output exactly or with regexes. Dump/load tests pipe dump files into `ldb load`; metadata tests compare parsed output from two commands; corruption tests overwrite or remove SST files and expect `checkconsistency` failure.

## State and Persistence
The suite creates real DB directories and verifies persistence across separate `ldb` processes. It covers WAL files, MANIFEST files, SST files, blob files, OPTIONS loading, external SST files, and backup-like dump/load artifacts. TTL tests depend on timestamp-suffixed values; transaction tests create data through TransactionDB modes and verify normal reads where supported.

## Dependencies and Integration Points
It depends on a built `./ldb` binary in the current working directory, shell utilities (`cat`, `grep`, `ls`, `cp`, `rm`), Python `unittest`, and RocksDB command output formats. It is a broad integration layer over the C++ ldb command implementation.

## Risks
The tests are output-format sensitive and use shell=True command strings, so quoting and platform differences can cause fragility. A duplicate `testInvalidCmdLines` name means the later definition overrides the earlier one. Corruption tests use globbed SST output and destructive file writes/removes within the temp DB. Regex parsing of metadata commands can break on harmless formatting changes.

## Test Signals
Passing this suite is strong evidence that the installed `ldb` binary behaves correctly for common CLI workflows, file-format dump paths, column-family management, blob support, transaction flags, and external SST ingestion.
