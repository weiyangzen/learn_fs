# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/volume/acl/TestOMVolumeAddAclRequest.java

## Purpose
This class tests `OMVolumeAddAclRequest`, ensuring preExecute sets modification time, successful validation appends an ACL to a volume, and missing volumes return the correct status.

## Important APIs and Types
It uses `OMVolumeAddAclRequest`, `OzoneAcl`, `OmVolumeArgs`, `OMRequestTestUtils.createVolumeAddAclRequest`, `OMClientResponse`, `OMResponse`, and volume metadata tables.

## Control Flow and State
`testPreExecute` creates an add-ACL request, records the original modification time, runs preExecute, and asserts the request changed and the new modification time is greater. `testValidateAndUpdateCacheSuccess` seeds user and volume rows, creates an access ACL for user `bilbo`, runs validation, expects `OK`, and asserts the volume's ACL list has exactly that ACL. `testValidateAndUpdateCacheWithVolumeNotFound` validates against a missing volume and expects `VOLUME_NOT_FOUND`.

## Dependencies and Integration Points
The class integrates the shared volume fixture, ACL protobuf construction, OM volume table mutation, and add-ACL response generation.

## Risks and Test Signals
Risks include not updating modification time, duplicate/incorrect ACL insertion, or returning success for a missing volume. Modification-time, status, and ACL-list assertions are the key signals.
