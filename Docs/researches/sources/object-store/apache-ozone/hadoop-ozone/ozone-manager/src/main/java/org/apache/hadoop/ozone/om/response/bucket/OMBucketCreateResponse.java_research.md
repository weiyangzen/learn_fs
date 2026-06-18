# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketCreateResponse.java

Purpose: `OMBucketCreateResponse` persists successful bucket creation and optional volume namespace usage updates.

Important APIs and types: It stores `OmBucketInfo` and optional `OmVolumeArgs`, annotates cleanup for `BUCKET_TABLE` and `VOLUME_TABLE`, and exposes `getOmBucketInfo`.

Control flow: On DB batch application it derives the bucket key and writes bucket info. If volume args are present, it also writes the volume table entry.

State and persistence behavior: It inserts a bucket-table row and may update volume-table quota/namespace state. Error constructor enforces non-OK status and stores null payloads.

Dependencies and integration points: It is paired with bucket create request logic and metadata-manager key derivation.

Risks and test signals: Tests should cover create with and without volume update, error no-op, cleanup table annotation, and correct volume/bucket keys.
