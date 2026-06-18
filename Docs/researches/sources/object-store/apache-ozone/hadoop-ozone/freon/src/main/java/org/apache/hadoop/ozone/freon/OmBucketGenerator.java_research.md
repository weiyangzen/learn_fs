## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketGenerator.java

Purpose: Freon subcommand `ombg`/`om-bucket-generator` that creates Ozone buckets directly through OM protocol.

Important APIs/types/functions: options configure volume and OM service ID. Overrides `allowDuration` to false. `call` ensures the volume exists and creates an OM client. `createBucket` builds `OmBucketInfo` with DISK storage and calls `createBucket`.

Control flow: initialize Freon, create Ozone client, ensure volume, create OM protocol translator, create timer, and run bucket creation tasks.

State and persistence behavior: persists Ozone bucket metadata under the target volume. Local state stores OM client and timer.

Dependencies and integration points: uses Ozone RPC client for volume existence and OM protocol for bucket creation.

Risks: duplicate bucket names fail unless previous runs use unique prefixes; duration disabled because repeated bucket namespace generation is count-based; OM client is manually closed in finally.

Test signals: bucket-create timer and resulting bucket count under the volume.
