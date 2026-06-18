# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorOm.java

Purpose: offline generator for Ozone Manager RocksDB metadata representing a volume, bucket, directory hierarchy, keys, and block locations.

Important APIs/types/functions: command `cgom`; options `--volume` and `--bucket`; `call`, `writeOmKeys`, `writeOmBucketVolume`, `addDirectoryKey`, `writeOmData`, and `commitAndResetOMKeyTableBatchOperation`.

Control flow: `call` forces single-thread Freon execution, opens the OM DB from `OMStorage.getOmDbDir`, creates/updates volume, user, and bucket rows, opens the key table, and runs `writeOmKeys`. Each container index maps to a container id, then the generator writes `getKeysPerContainer` key records in one batch. `writeOmData` builds one block location per key, derives L1/L2/L3 pseudo-directories from the local id, conditionally writes directory keys, and writes the file key.

State/persistence: directly mutates OM metadata tables (`VOLUME`, `USER`, `BUCKET`, `KEY`) through `OMDBDefinition`. The key path constant is hard-coded as `/vol1/bucket1/...` even though fields use `volumeName` and `bucketName`.

Dependencies/integration: OM DB definitions/codecs, `DBStoreBuilder`, `BatchOperation`, OM helper types, Ozone ACLs, replication configs, and Freon metrics.

Risks: offline-only DB writer; concurrent OM access would be unsafe. Hard-coded `keyName` prefix ignores non-default `--volume`/`--bucket` and can write inconsistent rows. Volume quota is fixed to 100 bytes, which may not reflect generated data. Replication metadata uses standalone factor three for keys while datanode placement is synthetic.

Test signals: no direct test in this subset. Useful tests should cover custom volume/bucket names, generated directory keys, batch contents, and DB reopen compatibility.
