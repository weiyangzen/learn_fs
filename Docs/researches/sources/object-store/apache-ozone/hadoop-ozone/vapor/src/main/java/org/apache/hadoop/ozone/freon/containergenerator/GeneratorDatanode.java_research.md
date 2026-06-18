# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorDatanode.java

Purpose: offline generator for Ozone datanode container files and block/chunk metadata.

Important APIs/types/functions: command `cgdn`; options `--datanodes`, `--index`, `--zero`, `--overlap`; `call`, `getScmIdFromStoragePath`, static `getPlacement`, `generateData`, `generatedRandomData`, `createContainer`, and `writeChunk`.

Control flow: `call` initializes Ozone config, block/chunk managers, storage dirs, VERSION metadata, `MutableVolumeSet`, checksum settings, and Freon timer, then runs `generateData`. For each requested container id, `getPlacement` decides whether the current datanode index stores it. Selected containers are created as `KeyValueContainer`s. For each block/key, the generator writes chunks up to `--key-size`, computes checksum before buffer consumption, writes the data and commit stages through `ChunkManager`, persists block metadata, and closes the container.

State/persistence: writes actual datanode container data/metadata under configured datanode storage volumes. Reads existing `hdds/VERSION` and SCM-specific directory names and uses persisted cluster/datanode IDs. `logCounter` simulates Ratis log indexes.

Dependencies/integration: Ozone container key-value implementation, chunk/block managers, storage-volume utilities, checksum config, HDDS storage dirs, Freon metrics, and the placement test.

Risks: intended for stopped/offline clusters; running against active datanode volumes could corrupt or conflict. `getPlacement` divides by `maxDatanodes / 3`, so fewer than three datanodes can divide by zero. `overlap` is not validated. Random-data generation comment says 4 bit but shifts bytes. Reusing `ByteBuffer` across write stages depends on chunk manager semantics.

Test signals: `TestGeneratorDatanode` verifies placement for 3 and 10 datanode layouts, including overlap 2. It does not cover storage writes, checksum/chunk persistence, invalid datanode counts, or overlap bounds.
