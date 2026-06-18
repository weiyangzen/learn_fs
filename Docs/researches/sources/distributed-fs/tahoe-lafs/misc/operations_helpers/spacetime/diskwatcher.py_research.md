# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/spacetime/diskwatcher.py

## Purpose

This Axiom model defines persisted disk usage samples for the diskwatcher subsystem and upgrades older samples to include total disk space.

## Important APIs, Types, and Functions

`Sample` is an `axiom.item.Item` with explicit `typeName = "diskwatcher_sample"` and `schemaVersion = 2`. Attributes are indexed `url`, indexed `when`, and integer `total`, `used`, and `avail`. `upgradeSample1to2(old)` calls `old.upgradeVersion` to add `total=0` while preserving existing fields. `registerUpgrader` registers the migration.

## Control Flow

Importing the module defines the item and registers the upgrader. Axiom invokes the upgrader when opening stores with version-1 `diskwatcher_sample` items.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is the Axiom store schema and sample rows. Dependencies are Axiom item/attributes/upgrades. Integration is diskwatcher storage and Munin plugins consuming its aggregated JSON. Risks include defaulting `total` to zero for upgraded historical samples, schema name compatibility with auto-generated old names, and Axiom dependency age. Tests should create a version-1 item in a store, run upgrade, and verify all fields and indexes.
