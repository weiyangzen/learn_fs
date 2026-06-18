# sources/storage-engines/rocksdb/tools/rocksdb_dump_test.sh

## Purpose
This shell smoke test verifies that a bundled sample dump can be imported with `rocksdb_undump`, exported with `rocksdb_dump --anonymous`, and compared byte-for-byte with the original dump.

## Important APIs, Types, and Functions
The script uses `mktemp -d` to create `TESTDIR`, sets `DUMPFILE=tools/sample-dump.dmp`, then invokes `./rocksdb_undump`, `./rocksdb_dump`, and `cmp`.

## Control Flow
It creates a temporary DB path, undumps the sample into `$TESTDIR/db`, dumps that DB back to `$TESTDIR/dump`, and compares the files. There is no explicit cleanup or shell `set -e`; failure depends on the final command status unless the caller runs with strict shell settings.

## State and Persistence
It writes a temporary DB and dump file under `${TMPDIR:-/tmp}`. The temp directory is not removed by the script, so repeated runs leave artifacts.

## Dependencies and Integration Points
It depends on built `rocksdb_undump` and `rocksdb_dump` binaries in the working directory and the sample dump at `tools/sample-dump.dmp`.

## Risks
Missing `set -e` means an early undump failure could be masked until `cmp`. There is no trap cleanup. The test is intentionally narrow and only covers anonymous round-tripping for one fixture.

## Test Signals
The key signal is `cmp` success, proving the sample dump can round-trip exactly through the dump/undump tools.
