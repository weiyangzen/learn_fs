<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMQuotaRepairResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMQuotaRepairResponse.java

Purpose: Persists repaired quota/accounting state for volumes and buckets produced by `OMQuotaRepairRequest`.

Important APIs/types/functions: Extends `OMClientResponse`. One constructor handles failure/update-only response with only `OMResponse`; the success constructor stores maps of volume names to `OmVolumeArgs` and `(volume,bucket)` pairs to `OmBucketInfo`. `addToDBBatch` rewrites bucket and volume rows.

Control flow and persistence: Iterates `volBucketInfoMap.values()` and writes each bucket under `getBucketKey(volumeName, bucketName)`, then iterates `volumeArgsMap.values()` and writes each volume to `VolumeTable` using `volArgs.getVolume()` as key. Cleanup metadata names `VOLUME_TABLE` and `BUCKET_TABLE`.

Dependencies and integration: Used by quota repair request processing after recalculating usage.

Risks and test signals: Volume-table keying should be verified because most volume responses use `getVolumeKey`. Null maps in the failure-style constructor would fail if `addToDBBatch` ran. Tests should cover multi-volume/bucket repair, empty maps, failure no-op lifecycle, and repaired quota values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMQuotaRepairResponse.java -->
