# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/VolumeManagerImpl.java

Purpose: `VolumeManagerImpl` implements read-only volume metadata and ACL checks over `OMMetadataManager`.

Important APIs and types: It implements `getVolumeInfo`, `listVolumes`, `getAcl`, and `checkAccess`. It uses `VOLUME_LOCK`, `USER_LOCK`, `OmVolumeArgs`, `OzoneObj`, `RequestContext`, `OzoneAclUtil`, and `OMException.ResultCodes`.

Control flow: `getVolumeInfo` requires a non-null volume, acquires `VOLUME_LOCK`, reads `volumeTable`, and throws `VOLUME_NOT_FOUND` if absent. `listVolumes` acquires `USER_LOCK` only for user-filtered listings and delegates to `metadataManager.listVolumes`. `getAcl` validates the resource type is volume, reads the volume under lock, and returns its ACL list. `checkAccess` reads the same volume and delegates ACL evaluation to `OzoneAclUtil.checkAclRights`, wrapping unexpected IO in an internal-error `OMException`.

State and persistence behavior: The class is stateless except for its metadata manager reference. It reads persistent volume metadata and does not write tables.

Dependencies and integration points: OM volume request handlers and ACL authorizer paths call this implementation. It relies on lock ordering enforced by OM lock trackers.

Risks and test signals: Returning the underlying ACL list may expose mutable metadata depending on `OmVolumeArgs` implementation. `listVolumes` only locks the user table, not all volume rows. Tests should cover missing volumes, invalid resource type, lock release on exceptions, ACL true/false results, and user-specific listing under concurrent volume changes.
