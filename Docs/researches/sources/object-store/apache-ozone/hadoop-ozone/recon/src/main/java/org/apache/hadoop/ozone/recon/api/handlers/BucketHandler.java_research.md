<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketHandler.java

## Purpose

`BucketHandler` is the abstract strategy layer that hides bucket-layout differences from namespace entity handlers.

## Important APIs and Types

Subclasses implement `determineKeyPath`, `calculateDUUnderObject`, `handleDirectKeys`, `getDirObjectId`, `getBucketLayout`, `getKeyInfo`, and `getDirInfo`. Static helpers include `buildSubpath`, `getKeyName`, and two `getBucketHandler` factories.

## Control Flow

The factory reads `OmBucketInfo` and returns an FSO, legacy, or OBS handler. Legacy buckets are routed to `LegacyBucketHandler` only when `OmConfig.Keys.ENABLE_FILESYSTEM_PATHS` is true; otherwise they are treated as object-store buckets through `OBSBucketHandler`.

## State and Persistence

The base class stores injected namespace and OM metadata managers. It writes nothing and reads volume/bucket IDs from OM metadata tables.

## Dependencies and Integration Points

It is used by `EntityHandler`, `OMDBInsightEndpoint`, and all entity handlers needing layout-specific path resolution or direct-key DU.

## Risks and Edge Cases

Factory behavior depends on OM configuration availability; if configuration is null it creates a default `OzoneConfiguration`, which can alter legacy semantics. Unsupported bucket layouts return null and become unknown paths. `bucketExists` uses skip-cache table reads.

## Test Signals

Tests should assert factory selection for FSO, legacy with filesystem paths on/off, OBS, null bucket info, unsupported layout, and helper path formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketHandler.java -->
