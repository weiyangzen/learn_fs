## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyGenerator.java

Purpose: Freon subcommand `ockg`/`ozone-client-key-generator` that writes full Ozone keys through the client API, optionally using Ratis streaming.

Important APIs/types/functions: options configure volume, bucket, key size, buffer size, OM service ID, replication, and `--enable-streaming/--stream`. Methods include `call`, `createKey`, `createKeyWithData`, and `createStreamKey`.

Control flow: initialize Freon, create content generator and metadata map, resolve replication config, ensure target bucket, obtain `OzoneBucket`, set `key-create` timer, and choose normal or stream task provider. Normal writes create a key output stream and write content inside tracing spans. Streaming writes force RATIS/THREE replication config and use `createStreamKey`.

State and persistence behavior: creates Ozone keys and writes data bytes. Local state includes bucket handle, content generator, metadata, timer, and replication config.

Dependencies and integration points: Ozone client object store, Ozone streaming output, tracing, `FreonReplicationOptions`, `ContentGenerator`.

Risks: streaming ignores user replication options and forces RATIS THREE; generated content is repeated from one buffer; duplicate key names fail unless prefix changes.

Test signals: pair with `OzoneClientKeyValidator`; assert key-create timer and readable generated keys.
