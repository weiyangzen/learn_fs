# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketDeleteResponse.java

Purpose: `OMBucketDeleteResponse` persists bucket deletion and optional volume namespace usage updates.

Important APIs and types: It stores volume and bucket names plus optional `OmVolumeArgs`, and cleans `BUCKET_TABLE` and `VOLUME_TABLE`.

Control flow: `addToDBBatch` deletes the bucket-table row by metadata-manager bucket key and writes updated volume args when provided.

State and persistence behavior: Successful response removes the bucket row and may persist volume quota counters. Error constructor stores no names and enforces non-OK.

Dependencies and integration points: It integrates bucket delete request validation, metadata-manager keying, and cache cleanup.

Risks and test signals: Tests should assert bucket deletion, volume update optionality, getters for names, and no writes on failed responses.
