# sources/storage-engines/rocksdb/tools/restore_db.sh

## Purpose
This tiny Bash wrapper restores the latest backup from a RocksDB backup directory into a DB directory by invoking `./ldb restore`.

## Important APIs, Types, and Functions
There are no functions. It validates that at least two arguments are present, assigns `backup_dir="$1"` and `db_dir="$2"`, logs the restore operation, and runs `./ldb restore --db="$db_dir" --backup_dir="$backup_dir"`.

## Control Flow
The script exits with usage status `1` when required arguments are missing. Otherwise it delegates all real work and exit behavior to `ldb restore`.

## State and Persistence
The target DB path can be created or overwritten according to `ldb restore` semantics. The script itself writes no metadata.

## Dependencies and Integration Points
It assumes `./ldb` exists in the current working directory and supports the `restore` command. It integrates with RocksDB backup/restore tooling through the ldb command surface.

## Risks
There is no validation that paths are safe, empty, local, or distinct. Additional restore options cannot be passed through. Running from the wrong directory fails or invokes the wrong `ldb` binary.

## Test Signals
No dedicated tests are present here. A practical signal is successful restore followed by `ldb checkconsistency` or application-level reads from the restored DB.
