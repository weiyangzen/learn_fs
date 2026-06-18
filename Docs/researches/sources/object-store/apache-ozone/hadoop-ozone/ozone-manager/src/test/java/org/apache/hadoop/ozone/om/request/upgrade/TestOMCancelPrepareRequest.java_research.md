# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/upgrade/TestOMCancelPrepareRequest.java

## Purpose
This class tests `OMCancelPrepareRequest`, ensuring cancel-prepare clears OM prepare state and is idempotent. It extends `TestOMKeyRequest`, reusing the OM request fixture and bucket layout helpers.

## Important APIs and Types
Key types are `OzoneManagerPrepareState`, `PrepareStatus`, `OMCancelPrepareRequest`, `OMOpenKeysDeleteRequest`, `OMClientResponse`, `CancelPrepareRequest`, `UserInfo`, `OMRequest`, and request `Type.CancelPrepare`.

## Control Flow and State
`testCancelPrepare` first asserts the manager is not prepared, calls `ozoneManager.getPrepareState().finishPrepare(LOG_INDEX)`, verifies prepared state, submits cancel prepare, verifies unprepared state, then submits cancel again to ensure no error. `assertPrepared` checks status `PREPARE_COMPLETED`, index value, marker-file existence, and that ordinary `CreateVolume` requests are blocked. `assertNotPrepared` checks status `NOT_PREPARED`, no prepare index, marker-file absence, and `CreateVolume` allowed.

`submitCancelPrepareRequest` pre-executes a cancel request, constructs `OMCancelPrepareRequest`, runs `validateAndUpdateCache`, and expects response status `OK`. `doPreExecute` uses `OMOpenKeysDeleteRequest.preExecute` to add user info, then asserts the request changed. `createCancelPrepareRequest` creates the protobuf request with explicit user name, host, and remote address.

## Dependencies and Integration Points
The test integrates OM prepare-state marker files, request admission checks, protobuf user-info handling, and cancel-prepare validation. The use of `OMOpenKeysDeleteRequest` for preExecute is unusual but verifies shared request-preExecute behavior sets user info.

## Risks and Test Signals
Risks include failing to remove the marker file, leaving OM in a request-blocking state, returning non-OK on repeated cancel, or not carrying user info through preExecute. The state assertions before and after each cancel are the core regression signals.
