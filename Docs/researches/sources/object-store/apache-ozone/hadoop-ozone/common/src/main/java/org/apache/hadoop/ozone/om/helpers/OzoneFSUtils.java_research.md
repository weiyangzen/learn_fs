<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFSUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFSUtils.java

## Purpose

`OzoneFSUtils` contains path, key, bucket-layout, snapshot-name, depth, and hsync feature helpers for Ozone file-system semantics.

## Important APIs, Types, And Functions

Important methods include `pathToKey`, `getParent`, `getImmediateChild`, `addTrailingSlashIfNeeded`, `isFile`, `isValidName`, `isValidKeyPath`, `validateBucketLayout`, `getFileName`, `isSibling`, `isAncestorPath`, `isImmediateChild`, `getParentDir`, `appendFileNameToKeyPath`, `getFileCount`, `removeTrailingSlashIfNeeded`, `generateUniqueTempSnapshotName`, `trimPathToDepth`, and `canEnableHsync`.

## Control Flow, State, And Persistence

The utility is stateless. Path validation rejects leading slashes for key paths, missing leading slashes for absolute names, `.`, `..`, `:`, embedded slash elements, and mid-path empty components. Bucket layout validation rejects object-store buckets for FS APIs. `canEnableHsync` gates hsync on both the hsync flag and HBase-enhancement allowance.

## Dependencies And Integration Points

It depends on Hadoop `Path`, Java NIO `Paths`, Ozone constants/config keys, `BucketLayout`, `SnapshotInfo`, `Time`, and `OMException`. It integrates with OzoneFS, FSO bucket operations, snapshot temp directory handling, list-status path trimming, and client/server hsync configuration.

## Risks And Test Signals

Java NIO path handling is platform-sensitive; tests should run path validation with slashes, trailing slashes, root, empty paths, and Windows-like colon inputs. Also test object-store bucket rejection, immediate child/sibling logic for root and relative paths, temp snapshot name uniqueness, and hsync gating when enhancement config differs client-side versus server-side.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneFSUtils.java -->
