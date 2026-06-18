## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/helper/SnapshotDiffObjectInfo.java

Purpose: small serializable value object for snapshot diff intermediate object metadata.

Important APIs and types: fields `objectId` and `key`; constructor; static `getCodec`; private protobuf conversion methods using `DelegatedCodec` and `Proto2Codec` over `SnapDiffObjectInfo`.

Control flow and persistence: codec serializes to/from OM storage protobuf fields `objectID` and `keyName`, enabling use as a RocksDB table value.

Dependencies and integration: schema definitions include this type for from-snapshot and to-snapshot object-info tables, though current `SnapshotDiffManager` uses raw byte maps for intermediate state to reduce serialization overhead.

Risks and test signals: fields are mutable but have no getters in this file, so practical use is codec-centered. Tests should round-trip object id and key through the codec and verify compatibility with protobuf defaults.
