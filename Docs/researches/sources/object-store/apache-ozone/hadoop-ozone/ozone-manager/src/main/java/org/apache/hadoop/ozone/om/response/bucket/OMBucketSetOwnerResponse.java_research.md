# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/OMBucketSetOwnerResponse.java

Purpose: `OMBucketSetOwnerResponse` persists bucket owner changes.

Important APIs and types: It stores `OmBucketInfo`, annotates `BUCKET_TABLE`, and overrides `checkAndUpdateDB` to require both status `OK` and response `success=true`.

Control flow: Same-owner requests can produce status OK but success false; the override avoids persisting in that no-op case. Otherwise it writes the bucket table entry.

State and persistence behavior: Successful owner changes update only the bucket table. Error/no-op cases do not write.

Dependencies and integration points: It matches request semantics from bucket owner update logic and OM response status/success conventions.

Risks and test signals: Tests should cover OK/success true writes, OK/success false no-op, failed response no-op, and bucket key correctness.
