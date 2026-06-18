# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestQuotaRepairTask.java

Purpose: Tests `QuotaRepairTask` and its generated `OMQuotaRepairRequest`/`OMQuotaRepairResponse` against object-store and FSO buckets plus old quota sentinel values. Important APIs and types include `QuotaRepairTask`, `OMQuotaRepairRequest`, `OMQuotaRepairResponse`, mocked `OzoneManagerRatisServer`, `BatchOperation`, `OmBucketInfo`, `OmVolumeArgs`, `OmKeyInfo`, and `OMRequestTestUtils`.

Control flow: The main test adds an OBS bucket with 10 keys and an FSO bucket with parent directories plus 10 files, zeros bucket usage, runs repair, captures the submitted Ratis request, validates it through OM request code, applies the response batch, and checks recomputed namespace/bytes. The old-version test creates volume/bucket quota values of `-2`, runs repair, applies the response, and expects migration to `-1`.

State and persistence behavior: It directly populates key/file/dir/bucket/volume tables and cache entries, then repairs bucket usage and quota flags via the same request/response flow used in OM. Dependencies are quota calculation, replication factor accounting, FSO namespace counting, Ratis submission, and DB batch persistence.

Risks: Direct table insertion bypasses normal request side effects by design. Test signals are successful repair future, captured request, updated OBS usage `10/30000`, FSO usage `13/10000`, and old quota flags converted to `-1`.
