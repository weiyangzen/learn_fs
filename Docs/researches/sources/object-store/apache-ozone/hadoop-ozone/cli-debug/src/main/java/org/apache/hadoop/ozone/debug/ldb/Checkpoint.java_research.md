# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/Checkpoint.java

Purpose: `Checkpoint` creates a RocksDB checkpoint from the database selected by the parent ldb command.

Important APIs and types: It extends `AbstractSubcommand`, implements `Callable<Void>`, uses parent `RDBParser`, `RocksDBUtils`, `ManagedRocksDB.openReadOnly`, and `ManagedCheckpoint`.

Control flow: The command lists column family descriptors, opens the DB read-only with handles, creates a managed checkpoint, writes it to `--output`, and prints the output path.

State and persistence behavior: It reads the source RocksDB and writes a checkpoint directory. It does not mutate the source DB.

Dependencies and integration points: It is a subcommand of `ozone debug ldb` and depends on RocksDB checkpoint APIs.

Risks: Output path validation and overwrite semantics are delegated to RocksDB. Column family handles are not explicitly closed in this file, relying on managed DB cleanup.

Test signals: Created checkpoint directory and success message.
