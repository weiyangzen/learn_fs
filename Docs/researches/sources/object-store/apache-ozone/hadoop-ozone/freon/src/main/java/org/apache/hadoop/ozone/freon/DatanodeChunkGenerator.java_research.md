## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DatanodeChunkGenerator.java

Purpose: Freon subcommand `dcg`/`datanode-chunk-generator` that writes raw chunks through Xceiver clients to one or more datanode pipelines.

Important APIs/types/functions: options include async mode, chunk size, pipeline IDs, and datanode host filters. Methods include `call`, `pipelineContainsDatanode`, `arePipelinesOrDatanodesProvided`, `runTest`, `writeChunk`, and `sendWriteChunkRequest`.

Control flow: reject secure clusters, parse comma-separated pipeline/datanode selectors, list SCM pipelines, initialize Freon, choose default first factor-three pipeline or selected pipelines containing IDs/hosts, acquire clients, prepare random payload and CRC32 checksum, then run write tasks. Each task uses container ID 1, local ID `stepNo % 20`, offset `(stepNo / 20) * chunkSize`, and sends sync or async `WriteChunk`, waiting for commit in async mode.

State and persistence behavior: writes chunk data into datanode container storage for fake block IDs. Local state stores Xceiver clients, payload, checksum, and timer.

Dependencies and integration points: SCM pipeline list, Xceiver client, datanode protobufs, checksum utilities.

Risks: selector loop only iterates `pipelinesFromCmd`, so datanode-only selection with an empty pipeline string depends on filtering behavior; hard-coded container 1; unsupported in secure clusters; async commit wait can block.

Test signals: paired with `DatanodeChunkValidator`; chunk-write metrics and successful raw reads validate behavior.
