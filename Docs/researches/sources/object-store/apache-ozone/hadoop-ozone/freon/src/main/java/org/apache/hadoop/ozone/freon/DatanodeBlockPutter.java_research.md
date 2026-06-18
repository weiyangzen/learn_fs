## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeBlockPutter.java

Purpose: Freon subcommand `dbp`/`datanode-block-putter` that issues raw `PutBlock` datanode commands with fake chunk metadata to a Ratis/THREE pipeline.

Important APIs/types/functions: options include chunks per block, fake chunk size, and optional pipeline ID. `call` sets up clients and checksum data; `putBlock` builds `DatanodeBlockID`, `BlockData`, chunk list, and `ContainerCommandRequestProto`.

Control flow: initialize Freon, reject secure clusters, create SCM client, find pipeline, acquire Xceiver client, generate random data and CRC32 checksum protobuf, then run `putBlock` tasks. Each task uses container ID `1L`, local ID and BCSID from task number, and sends a `PutBlock` command timed by metrics.

State and persistence behavior: mutates datanode/Ratis metadata by committing fake block records for container 1; chunks do not actually exist. Local state is client, timer, and checksum protobuf.

Dependencies and integration points: direct HDDS datanode protocol protobufs, SCM pipeline lookup, Xceiver client, Ozone security check, and `BaseFreonGenerator.findPipelineForTest`.

Risks: unsupported in secure environments; hard-coded container ID 1 and fake chunks can fail if the container is absent or validation changes; fake metadata can pollute test clusters.

Test signals: useful for stress testing datanode block metadata path and measuring `put-block` timer counts.
