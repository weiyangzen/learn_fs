<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatus.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatus.java

## Purpose

`OzoneFileStatus` is the full file-status model returned by Ozone FS list and lookup APIs. It wraps `OmKeyInfo`, directory/file state, and block size.

## Important APIs, Types, And Functions

The class exposes `getKeyInfo`, `getBlockSize`, `getTrimmedName`, `getPath`, `isDirectory`, `isFile`, `getProtobuf`, `getFromProtobuf`, `equals`, `hashCode`, and `toString`. A null `keyInfo` represents the synthetic root directory.

## Control Flow, State, And Persistence

Instances are transient protocol results. `getProtobuf` serializes block size, directory flag, and optional key info using the caller's client version. `getFromProtobuf` rebuilds status from `OzoneFileStatusProto`.

## Dependencies And Integration Points

It depends on `OmKeyInfo`, Ozone URI delimiter constants, and `OzoneFileStatusProto`. It is returned by `IOmMetadataReader`/`OzoneManagerProtocol.listStatus` and consumed by OzoneFS clients.

## Risks And Test Signals

`getTrimmedName`, `equals`, and `hashCode` assume non-null `keyInfo`; root status can throw if compared or hashed through those paths. Tests should cover root status, trailing slash trimming, protobuf round trips by client version, directory/file flags, and equality for same key name with different block metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFileStatus.java -->
