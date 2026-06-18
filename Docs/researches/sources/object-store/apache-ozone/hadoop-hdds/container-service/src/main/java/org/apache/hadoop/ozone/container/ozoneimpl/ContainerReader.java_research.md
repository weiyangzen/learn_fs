## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerReader.java

Purpose: Reads container metadata from an HDDS volume at datanode startup/load time, reconstructs in-memory container state, verifies layout, handles stale/deleted containers, and resolves duplicates.

Important APIs and functions: `run()` reads a volume and marks it failed on fatal errors. `readVolume()` finds cluster/current/container directories and calls `verifyContainerFile()`. `verifyAndFixupContainerData()` parses key-value container data, handles RECOVERING/DELETED state, matches EC replica index with witnessed metadata, adds containers, commits space, and resolves duplicates. `resolveDuplicate()` chooses between duplicate Ratis containers by CLOSED state and BCSID. `cleanupContainer()` removes persistent container data and calls `delete()`.

Control flow and state: The reader is bound to one `HddsVolume`, `ContainerSet`, config, volume set, and `shouldDelete` flag. It supports old SCM ID directories before SCM HA finalization. Recovering Ratis containers may be deleted, while EC recovering containers are marked unhealthy and loaded. Duplicate EC containers are left on disk with first loaded winning.

Persistence and dependencies: Reads `.container` YAML files, parses KV metadata, opens witnessed-container DB for EC matching, updates committed volume space, removes stale/deleted container directories/DB rows through `KeyValueContainerUtil`, and mutates `ContainerSet`.

Risks: Directory scanning catches broad throwables per container and can skip corrupt containers. Duplicate resolution deletes one copy for Ratis containers based on state/BCSID, so bad metadata can remove the desired copy. EC matching can ignore an on-disk container if witnessed DB replica index differs. `shouldDelete` heavily changes behavior.

Test signals: Empty/unformatted volume, old SCM ID directory, missing cluster ID dir, missing/corrupt `.container` file, KV parse fixups, recovering/deleted handling with `shouldDelete`, EC replica index mismatch, duplicate Ratis and EC containers, commit/release space, and volume failure on top-level errors.
