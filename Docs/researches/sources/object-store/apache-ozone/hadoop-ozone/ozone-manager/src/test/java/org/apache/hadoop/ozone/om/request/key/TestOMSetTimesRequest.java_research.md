# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMSetTimesRequest.java

Purpose: verifies `OMKeySetTimesRequest` updates key modification time for the default key layout. It extends `TestOMKeyRequest` and provides reusable hooks overridden by the FSO subclass.

Important APIs and types: `OMKeySetTimesRequest`, protobuf `SetTimesRequest`, `KeyArgs`, `OMClientResponse`, `OMResponse`, and `OMRequestTestUtils.addKeyToTable`. The helper `createSetTimesKeyRequest` embeds volume, bucket, key, mtime, and atime into an `OMRequest` with command type `SetTimes`.

Control flow: `testKeySetTimesRequest` creates the volume/bucket, adds a closed key to the key table, invokes `executeAndReturn(2000)`, then reads the key table and checks `modificationTime == 2000`. It then calls `executeAndReturn(-1)` and asserts the previous mtime remains unchanged, documenting that negative mtime means no modification-time update.

State and persistence behavior: the request uses the key table for the active bucket layout. The test inspects `omMetadataManager.getKeyTable(getBucketLayout()).get(ozoneKey)` after `validateAndUpdateCache`; it does not call response batch persistence, so it validates cache-visible behavior in the request path.

Dependencies and integration points: `preExecute` is called before validation, then the returned request is wrapped in a new `OMKeySetTimesRequest`. `addKeyToTable` uses RATIS replication config and transaction ID `1L`.

Risks covered: accidentally treating `-1` as a literal timestamp, not setting a response, wrong command status, and failure to find the key under the selected bucket layout. The base class does not cover directories; the FSO subclass adds that path.

Test signals: response contains `SetTimesResponse`, status is `OK`, and key table modification time changes only for non-negative mtime.
