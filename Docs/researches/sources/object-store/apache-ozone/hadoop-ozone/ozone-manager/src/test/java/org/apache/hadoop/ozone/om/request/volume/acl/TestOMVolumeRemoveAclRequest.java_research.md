# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/volume/acl/TestOMVolumeRemoveAclRequest.java

## Purpose
This class tests `OMVolumeRemoveAclRequest`, validating modification-time rewriting, successful ACL removal from a volume, and missing-volume failure behavior.

## Important APIs and Types
It uses `OMVolumeRemoveAclRequest`, `OMVolumeAddAclRequest` as setup, `OzoneAcl`, `OmVolumeArgs`, `OMRequestTestUtils`, `OMClientResponse`, and `OMResponse`.

## Control Flow and State
`testPreExecute` checks preExecute produces a modified request with a greater modification time. `testValidateAndUpdateCacheSuccess` seeds a volume, first adds a full access ACL using `OMVolumeAddAclRequest`, verifies add success, then constructs and validates a remove-ACL request. Before removal the volume ACL list contains the target ACL; after validation the response is `OK` and the ACL list is empty. `testValidateAndUpdateCacheWithVolumeNotFound` expects `VOLUME_NOT_FOUND` for a missing volume.

## Dependencies and Integration Points
The class integrates add/remove ACL request behavior, volume table persistence, and shared ACL parsing. It verifies remove semantics on a realistically added ACL rather than a hand-mutated list.

## Risks and Test Signals
Risks include remove not matching access-scope ACLs, leaving stale ACLs, not updating modification time, or accepting missing volumes. The before/after ACL-list assertions and statuses catch these issues.
