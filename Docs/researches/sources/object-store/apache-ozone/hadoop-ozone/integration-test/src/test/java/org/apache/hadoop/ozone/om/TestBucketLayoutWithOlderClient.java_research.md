# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucketLayoutWithOlderClient.java

## Purpose
This abstract non-HA integration test verifies bucket-layout behavior for older clients. It confirms modern client bucket creation follows explicit/default layout rules, while a manually constructed legacy-version `CreateBucket` request without bucket layout is interpreted as `LEGACY`.

## Important APIs, Types, and Functions
- `init()` stores the cluster reference and opens an Ozone client.
- `testCreateBucketWithOlderClient()` creates buckets through modern client helpers, constructs an `OMRequest` with `ClientVersion.DEFAULT_VERSION`, submits it directly through OM server protocol, and checks stored `OmBucketInfo`.
- `cleanup()` closes the client.

## Control Flow
The test reads the OM default bucket layout, creates a bucket without explicit layout and asserts the default, creates explicit FSO and OBS buckets and asserts those layouts, then builds a protobuf `CreateBucketRequest` that omits layout and uses an older client version. After setting `UserInfo`, it submits the request directly to `OzoneManager.getOmServerProtocol().submitRequest` and verifies the persisted bucket layout is `LEGACY`.

## State and Persistence Behavior
Bucket metadata in OM is the core state. The test toggles `OzoneManager.setTestSecureOmFlag(true)` before direct request submission, and the resulting bucket row must contain the legacy layout.

## Dependencies and Integration Points
Integrates `ClientVersion`, OM protobuf request/response types, secure OM test flag, `UserGroupInformation`, `TestDataUtil`, `BucketLayout`, and direct OM server protocol submission.

## Risks and Test Signals
Risks include coupling to protobuf request defaults and global secure-OM test flag state. Signals are response status `OK` and stored `OmBucketInfo.getBucketLayout()` equal to `LEGACY` for the older request.
