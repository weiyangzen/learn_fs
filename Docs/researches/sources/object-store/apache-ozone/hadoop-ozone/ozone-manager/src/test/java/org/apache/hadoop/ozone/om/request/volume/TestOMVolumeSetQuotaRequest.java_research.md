# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/volume/TestOMVolumeSetQuotaRequest.java

## Purpose
This class tests `OMVolumeSetQuotaRequest`, covering normal quota mutation, missing-volume and invalid-owner-payload failures, byte-quota validation against bucket quotas, namespace-quota validation against bucket count, and link-bucket quota handling.

## Important APIs and Types
It uses `OMVolumeSetQuotaRequest`, `OmVolumeArgs`, `OmBucketInfo`, `OMRequestTestUtils`, `OMClientResponse`, `OzoneConsts.GB`, and `GenericTestUtils.LogCapturer`.

## Control Flow and State
`testPreExecute` confirms set-quota requests are rewritten. `testValidateAndUpdateCacheSuccess` seeds user and volume rows, records previous byte and namespace quotas, validates a request, checks response `OK`, and asserts both quotas changed plus modification time is not earlier than creation time. Missing volume returns `VOLUME_NOT_FOUND`. Sending an owner-style set-property request into quota handling returns `INVALID_REQUEST`.

Quota-specific tests seed volumes and buckets. When total bucket byte quota is 8 GB and requested volume quota is 5 GB, validation returns `QUOTA_EXCEEDED`, logs a failure message, and includes an explanatory response message. If a bucket has no quota set, setting volume quota fails with `QUOTA_ERROR`. Link buckets are excluded from quota aggregation so a source bucket plus link bucket can still allow a 5 GB volume quota. Namespace quota below existing bucket count returns `QUOTA_EXCEEDED` with a namespace-specific message.

## Dependencies and Integration Points
The class integrates volume table state, bucket table scans, quota semantics for byte and namespace quotas, linked-bucket metadata, logging, and set-property protobuf handling.

## Risks and Test Signals
Risks include counting link buckets incorrectly, allowing volume quotas below bucket totals, accepting quotas when bucket quotas are unset, or applying owner payloads as quota updates. Status, response message, log, and table assertions provide signals.
