# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconDBProvider.java

Purpose: Provides the singleton Recon internal `DBStore`, supports staged DB creation for snapshot rebuilds, and swaps a staged DB into the live DB path.

Important APIs: `getDbStore`, `getStagedReconDBProvider`, `provideReconDB`, `replaceStagedDb`, `close`, and static `truncateTable`. `getStagedReconDBProvider` deletes any stale `.staged` DB and opens a fresh one. `replaceStagedDb` closes the staged and live stores, renames the live DB to `.backup`, renames staged into the live name, then reopens.

Control flow and persistence: startup recovers old last-known Recon DB paths from `ReconUtils.getLastKnownDB`. If the live DB is missing but a `.backup` exists, it restores the backup. DB open delegates to `DBStoreBuilder.createDBStore(configuration, new ReconDBDefinition(dbName))`.

Dependencies and integration: depends on `OzoneConfiguration`, `ReconUtils`, Apache Commons `FileUtils`, and local filesystem atomic moves. Managers are reinitialized against this provider after DB replacement.

Risks: `replaceStagedDb` recovery assumes the failure mode leaves enough paths to move back; partial filesystem failures can still strand `.staged` or `.backup` directories. `truncateTable` deletes row by row and is expensive for large column families. Atomic moves may fail across filesystems, so the configured DB directory must keep staged and live DBs on the same mount.

Test signals: `TestReconDBProvider` should cover initialization and provider binding. Additional valuable tests are interrupted replacement, backup restoration, stale staged cleanup, and `truncateTable` behavior on null and populated tables.
