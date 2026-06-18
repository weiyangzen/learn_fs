# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMMetadataStore.java

## Purpose

`SCMMetadataStore` is the central interface for SCM persistent metadata tables and lifecycle.

## Important APIs, Types, and Functions

Lifecycle methods are `start(OzoneConfiguration)` and `stop()`. Table accessors include deleted block transactions, valid certs, valid SCM certs, pipelines, containers, sequence IDs, move records, meta key/value strings, and stateful service config. It also exposes `getStore()` for testing and `getBatchHandler()`.

## Control Flow

Implementations initialize the underlying `DBStore`, construct typed tables/codecs, and return handles for managers to read/write. Batch handlers coordinate atomic updates where supported.

## State and Persistence Behavior

All table accessors represent persistent SCM RocksDB state: containers, pipelines, certificates, delete transactions, sequence IDs, move plans, upgrade/layout metadata, and service configs.

## Dependencies and Integration Points

It extends `DBStoreHAManager` and is consumed by SCM container, pipeline, security, HA, upgrade, and balancing managers.

## Risks and Test Signals

Schema/table compatibility is critical across upgrades and HA snapshots. Tests should verify table definitions/codecs, start/stop lifecycle, batch atomicity, checkpoint/HA integration, and persistence across restart.
