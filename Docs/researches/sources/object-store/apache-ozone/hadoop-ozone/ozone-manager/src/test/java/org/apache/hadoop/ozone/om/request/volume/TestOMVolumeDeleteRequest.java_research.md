# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/volume/TestOMVolumeDeleteRequest.java

## Purpose
This class tests `OMVolumeDeleteRequest`, ensuring volume delete requests are pre-executed, remove volume/user index rows when valid, and reject missing or non-empty volumes.

## Important APIs and Types
It uses `OMVolumeDeleteRequest`, `DeleteVolumeRequest`, `OMClientResponse`, `OmBucketInfo`, `OMRequestTestUtils`, and protobuf statuses `OK`, `VOLUME_NOT_FOUND`, and `VOLUME_NOT_EMPTY`.

## Control Flow and State
`testPreExecute` builds a delete-volume OM request, runs preExecute, and asserts the request changes, primarily due to user/timestamp metadata. `testValidateAndUpdateCacheSuccess` adds a volume and owner user record to DB, verifies both exist, validates delete, expects `OK`, removes the volume name from the owner's persisted list, and verifies the volume table row is gone. `testValidateAndUpdateCacheWithVolumeNotFound` validates a delete for a missing volume and expects `VOLUME_NOT_FOUND`. `testValidateAndUpdateCacheWithVolumeNotEmpty` creates a bucket under the volume before delete and expects `VOLUME_NOT_EMPTY`.

## Dependencies and Integration Points
The tests integrate volume table, user table, bucket table emptiness checks, and response status generation. They rely on the base volume fixture for temporary metadata manager and mocked OM services.

## Risks and Test Signals
Risks include deleting non-empty volumes, not removing the user-volume reverse index, deleting missing volumes as success, or failing to rewrite request metadata. Table presence/absence and status assertions provide the signals.
