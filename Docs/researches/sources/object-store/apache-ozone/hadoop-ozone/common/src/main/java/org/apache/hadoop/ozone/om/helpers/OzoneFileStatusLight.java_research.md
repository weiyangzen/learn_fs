<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatusLight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatusLight.java

## Purpose

`OzoneFileStatusLight` is a lightweight version of `OzoneFileStatus` that carries `BasicOmKeyInfo` instead of full block/key metadata to reduce list-status response size.

## Important APIs, Types, And Functions

It provides the same high-level API shape as `OzoneFileStatus`: key info and block-size getters, path/name helpers, `isDirectory`, `isFile`, `getProtobuf`, `getFromProtobuf`, equality/hash/toString, and static `fromOzoneFileStatus`.

## Control Flow, State, And Persistence

Instances are transient list-status results. Protobuf conversion uses `OzoneFileStatusProtoLight`, storing basic key info plus volume and bucket names. `fromOzoneFileStatus` extracts a `BasicOmKeyInfo` from full key info when possible.

## Dependencies And Integration Points

It depends on `BasicOmKeyInfo`, Ozone URI delimiter constants, and lightweight status protobufs. It integrates with `OzoneManagerProtocol.listStatusLight` and clients that need directory listings without block locations.

## Risks And Test Signals

Like the full status class, root handling can be fragile in equality and trimmed-name paths when `keyInfo` is null. Tests should cover conversion from full status, protobuf round trips, root and directory entries, trailing slash trimming, and preservation of volume/bucket names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatusLight.java -->
