## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmKeyGenerator.java

Purpose: Freon subcommand `omkg`/`om-key-generator` that creates key metadata directly in OM without writing data blocks.

Important APIs/types/functions: options configure volume, bucket, replication, and OM service ID. `call` ensures volume/bucket and creates OM client. `createKey` builds `OmKeyArgs`, opens a key, then commits it.

Control flow: initialize Freon, parse replication, ensure bucket via Ozone client, create OM protocol client, create `key-create` timer, and run tasks. Each task uses current user ACLs, empty location info, generated key name, and optional replication config.

State and persistence behavior: creates OM key metadata entries with no block locations. Local state stores OM client, timer, and replication config.

Dependencies and integration points: Ozone OM protocol, Ozone ACL utilities, user group information, `FreonReplicationOptions`.

Risks: keys without location info are synthetic and may not behave like fully written keys; duplicate names fail; current user/ACL behavior depends on security config.

Test signals: OM metadata key counts and timer; lookup/list commands can consume generated keys for metadata-only benchmarks.
