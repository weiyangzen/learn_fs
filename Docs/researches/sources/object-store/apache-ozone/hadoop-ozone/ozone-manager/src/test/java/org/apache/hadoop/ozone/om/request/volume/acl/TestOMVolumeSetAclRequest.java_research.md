# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/volume/acl/TestOMVolumeSetAclRequest.java

## Purpose
This class tests `OMVolumeSetAclRequest`, ensuring full ACL replacement sets modification time, persists both access and default ACLs, and fails cleanly when the volume does not exist.

## Important APIs and Types
It uses `OMVolumeSetAclRequest`, Guava `Lists`, `OzoneAcl`, `OmVolumeArgs`, `OMRequestTestUtils.createVolumeSetAclRequest`, `OMClientResponse`, and `OMResponse`.

## Control Flow and State
`testPreExecute` records original modification time, runs preExecute, asserts request inequality, and checks the new modification time is greater. `testValidateAndUpdateCacheSuccess` seeds a volume, builds two ACLs (`user:bilbo:rw[ACCESS]` and `group:admin:rwdlncxy[DEFAULT]`), validates the set-ACL request, expects `OK`, and asserts the volume ACL list has exactly two entries containing both ACLs. `testValidateAndUpdateCacheWithVolumeNotFound` expects `VOLUME_NOT_FOUND`.

## Dependencies and Integration Points
The class integrates volume metadata mutation, Ozone ACL parsing/scope handling, request preExecute timestamp updates, and set-ACL response generation.

## Risks and Test Signals
Risks include dropping default ACLs, appending instead of replacing, not updating timestamps, or succeeding for missing volumes. The content-based ACL assertions and status checks provide coverage.
