# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMQuotaRepairRequest.java

Purpose: `OMQuotaRepairRequest` handles an administrative repair operation that updates bucket used bytes/namespace counts and can migrate old quota sentinel values on buckets and volumes.

Important APIs and types: It extends `OMClientRequest`, reads `QuotaRepairRequest`, uses `BucketQuotaCount`, updates `OmBucketInfo` and `OmVolumeArgs`, returns `OMQuotaRepairResponse`, and uses `BUCKET_LOCK` and `VOLUME_LOCK`.

Control flow: `preExecute` creates the request user and rejects non-admin callers when admin authorization is enabled. `validateAndUpdateCache` iterates bucket count entries, calls `updateBucketInfo`, optionally calls `updateOldVolumeQuotaSupport`, builds a success response, and records updated bucket/volume maps for response batch persistence.

State and persistence behavior: Bucket repair increments used bytes and namespace, optionally rewrites `OLD_QUOTA_DEFAULT` to `QUOTA_RESET`, and writes bucket table cache entries at the transaction index. Volume migration scans the volume table and writes cache entries for volumes with old quota sentinels. The response persists the collected maps to DB.

Dependencies and integration points: It integrates quota repair RPC payloads, admin authorization, OM metadata tables, table iterators, cache values, and quota constants.

Risks and test signals: Risks include concurrent deletion during repair, partial progress across many buckets, and scanning the full volume table. Tests should cover admin denial, deleted bucket tolerance, old quota conversion, lock release, and response DB batch contents.
