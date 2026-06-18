# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/volume/TestOMVolumeSetOwnerRequest.java

## Purpose
This class tests `OMVolumeSetOwnerRequest`, the set-volume-property path that transfers volume ownership between users. It also verifies invalid quota-shaped requests are rejected by owner handling.

## Important APIs and Types
It uses `OMVolumeSetOwnerRequest`, `OMVolumeSetQuotaRequest` for preExecute in one test, `OMRequestTestUtils.createSetVolumePropertyRequest`, `PersistedUserVolumeInfo`, `OMClientResponse`, and volume/user metadata tables.

## Control Flow and State
`testPreExecute` builds an owner-change request but instantiates `OMVolumeSetQuotaRequest` for preExecute and asserts the request changes, reflecting shared set-property timestamp logic. `testValidateAndUpdateCacheSuccess` seeds a volume owned by `user1`, requests owner `user2`, validates, and checks status `OK`, volume table owner change, modification time >= creation time, new owner's user table contains the volume, and old owner's list is empty. `testValidateAndUpdateCacheWithVolumeNotFound` expects `VOLUME_NOT_FOUND`. `testInvalidRequest` sends a quota-style set-property request to owner handling and expects `INVALID_REQUEST`.

`testOwnSameVolumeTwice` executes the same owner transfer twice. First response is `OK` and success true; second response is `OK` with success false, and the new owner's volume list contains no duplicates.

## Dependencies and Integration Points
The tests integrate volume table mutation, user-to-volume reverse index maintenance, set-property request protobufs, and idempotency behavior.

## Risks and Test Signals
Risks include duplicate volume names in user lists, forgetting to remove old owner mappings, treating repeated owner changes as hard failures, or accepting quota payloads in owner code. User table and response success/status assertions catch these regressions.
