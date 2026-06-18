## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/FollowerReader.java

Purpose: Freon subcommand `fr`/`follower-reader` that repeatedly reads metadata size of the same key through multiple Ozone clients, intended to test OM follower/read performance.

Important APIs/types/functions: options configure volume, bucket, and key. `call` creates one `OzoneClient` per Freon thread and runs `readKeySize`; `readKeySize` selects a client by counter and calls `getKey(keyName).getDataSize()`.

Control flow: initialize Freon, create Ozone configuration, allocate clients, create timer, and run threaded tasks. Each task is timed under `follower-read`.

State and persistence behavior: read-only Ozone metadata calls; local state is the client list and timer.

Dependencies and integration points: uses `BaseFreonGenerator.createOzoneClient` and Ozone object store APIs.

Risks: clients are not closed in `call`, creating a resource leak in long runs; `omServiceID` is a private field fixed to null with no CLI option; target key must already exist.

Test signals: useful for measuring key metadata read throughput; should be paired with pre-created volume/bucket/key.
