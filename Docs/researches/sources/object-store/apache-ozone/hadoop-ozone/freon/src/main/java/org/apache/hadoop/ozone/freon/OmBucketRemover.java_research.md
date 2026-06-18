## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketRemover.java

Purpose: Freon subcommand `ombr`/`om-bucket-remover` that deletes generated Ozone buckets through OM protocol.

Important APIs/types/functions: options configure volume and OM service ID. `call` creates OM client and runs `removeBucket`; `removeBucket` calls `deleteBucket(volumeName, generateBucketName(index))`.

Control flow: initialize Freon, create Ozone configuration, create OM client, start `bucket-remove` timer, run tests, close OM client.

State and persistence behavior: deletes bucket metadata from the target volume. Local state stores OM client and timer.

Dependencies and integration points: intended to clean up or benchmark buckets created by `OmBucketGenerator`.

Risks: delete fails for non-empty or missing buckets; unlike generator it does not ensure volume existence; failures stop early unless `--fail-at-end` is set.

Test signals: bucket-remove timer, absent buckets after run, and expected failures for non-empty buckets.
