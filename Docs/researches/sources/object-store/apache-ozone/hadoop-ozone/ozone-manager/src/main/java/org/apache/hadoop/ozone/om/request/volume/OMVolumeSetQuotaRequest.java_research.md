# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeSetQuotaRequest.java

Purpose: `OMVolumeSetQuotaRequest` validates and stages updates to volume space and namespace quotas.

Important APIs and types: It handles `SetVolumePropertyRequest` quota fields, returns `OMVolumeSetQuotaResponse`, uses `OmVolumeArgs`, `OmBucketInfo`, `OzoneConsts.QUOTA_RESET`, and `OMException.ResultCodes.QUOTA_ERROR`/`QUOTA_EXCEEDED`.

Control flow: `preExecute` stamps modification time and checks WRITE ACL. `validateAndUpdateCache` rejects requests with neither quota field, acquires the volume lock, loads current volume info, validates byte quota against all non-link buckets and namespace quota against bucket count, applies valid fields, sets modification/update ID, and stages the volume-table cache entry.

State and persistence behavior: Only the volume table is updated. Invalid values below reset or equal zero are ignored by validation helpers; hard violations throw and produce error responses. The response persists the updated `OmVolumeArgs`.

Dependencies and integration points: It depends on `OMMetadataManager.listBuckets`, bucket quota semantics, volume ACL/audit, and request metrics.

Risks and test signals: Risks include expensive full bucket listing, behavior when one quota field is invalid but the other is valid, and link-bucket quota exclusion. Tests should cover quota reset, buckets without quota, total bucket quota exceeding volume quota, namespace lower than bucket count, and audit/metric failures.
