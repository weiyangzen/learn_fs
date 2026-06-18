<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmVolumeArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmVolumeArgs.java

## Purpose

`OmVolumeArgs` is the main persisted and protocol-facing metadata object for an Ozone volume. It stores admin, owner, volume name, creation/modification time, quota values, namespace usage, ACLs, object/update IDs, metadata, and a reference count used to track mounts or links.

## Important APIs, Types, And Functions

The class extends `WithObjectID` and implements `CopyObject`. Important methods include `getCodec`, getters, `getDefaultAcls`, equality by object ID, `getProtobuf`, `builderFromProtobuf`, `getFromProtobuf`, `toAuditMap`, and `copyObject`. The nested `Builder` supports quota, namespace, ACL, object/update ID, metadata, and ref-count mutation with validation.

## Control Flow, State, And Persistence

OM builds instances for create/update/read volume paths. `CODEC` delegates RocksDB persistence through `VolumeInfo` protobuf. `getProtobuf` writes all durable fields and fills zero creation time with current time. `builderFromProtobuf` reconstructs metadata and ACL lists. Builder validation rejects missing admin/owner/volume and negative ref counts while inherited `WithObjectID.Builder` guards object ID immutability and update ID monotonicity.

## Dependencies And Integration Points

It depends on Ozone constants, audit interfaces, `OzoneAcl`, `AclListBuilder`, `OzoneAclUtil`, `KeyValueUtil`, HDDS DB codecs, and `VolumeInfo` protobuf. It is central to volume APIs, S3 volume context, quota repair, ACL enforcement, OM metadata tables, audit logging, and service/client protocol translators.

## Risks And Test Signals

`copyObject()` returns `this`, relying on immutability of the object and immutable ACL list. Incorrect quota sentinel handling or creation-time defaults can affect upgrade compatibility. Tests should cover protobuf/codec round trips, ACL preservation, ref-count increment/decrement validation, object/update ID validation, audit map fields, and volume equality semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmVolumeArgs.java -->
