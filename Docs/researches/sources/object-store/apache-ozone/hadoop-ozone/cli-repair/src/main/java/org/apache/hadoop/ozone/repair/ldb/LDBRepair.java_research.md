## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/LDBRepair.java

Purpose: top-level `ozone repair ldb` command container for generic RocksDB/LDB operational repair utilities.

Important APIs and control flow: annotated with picocli `@Command(name = "ldb")`, registers `RocksDBManualCompaction` as its only subcommand, and implements `RepairSubcommand`. `@MetaInfServices(RepairSubcommand.class)` makes it discoverable by the repair CLI service-loader mechanism.

State and dependencies: no direct state or persistence. It depends on picocli and `hdds-cli` service-provider conventions to attach to the `OzoneRepair` command graph.

Risks and test signals: any missing subcommand registration would hide the compaction tool from users. `TestOzoneRepair.subcommandsSupportDryRun` walks command metadata, while `TestLdbRepair` exercises the registered compaction command directly.
