# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/TransactionInfoRepair.java

Purpose: `TransactionInfoRepair` updates the highest term/index stored in the transaction info table of an offline OM or SCM RocksDB.

Important APIs and types: It extends `RepairTool`, accepts required `--db`, `--term`, and `--index`, uses `ManagedRocksDB`, `RocksDBUtils`, `TransactionInfo`, `StringCodec`, `OMDBDefinition.TRANSACTION_INFO_TABLE_DEF`, and `SCMDBDefinition.TRANSACTIONINFO`.

Control flow: `execute` opens the DB with latest options, determines the target column family from the parent command name (`om` or `scm`), resolves the column family handle, reads and logs original transaction info, builds a new `TransactionInfo`, and writes it unless dry-run is active. RocksDB resources and column family handles are closed in `finally`.

State and persistence behavior: This is a mutating offline repair unless `--dry-run` is set. It writes the `TRANSACTION_INFO_KEY` value in the selected column family. It requires the relevant OM or SCM service to be offline through `RepairTool`.

Dependencies and integration points: It is intended for repair command parents named `om` or `scm`; `serviceToBeOffline` also uses that parent name to select the service.

Risks: Parent-name coupling can fail if command names change. Input term/index are described as non-zero but not validated. Opening with empty column-family descriptor list relies on RocksDB utility behavior. Incorrect values can make Ratis metadata inconsistent.

Test signals: Tests should cover OM and SCM column family selection, dry-run no-write, actual write and reread, missing column family, invalid parent command, running-service gate, and zero/negative term-index validation if added.
