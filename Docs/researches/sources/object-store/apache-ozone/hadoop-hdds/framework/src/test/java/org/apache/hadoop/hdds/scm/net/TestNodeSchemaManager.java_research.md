# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNodeSchemaManager.java

## Purpose

This test verifies `NodeSchemaManager` initialization from config, layer-cost access, schema-load failure handling, and topology path completion defaults.

## Important APIs, Types, And Functions

It uses `NodeSchemaManager.getInstance`, `init(OzoneConfiguration)`, `getCost`, `getMaxLevel`, and `complete`. Config key `OZONE_SCM_NETWORK_TOPOLOGY_SCHEMA_FILE` points to `good.xml`.

## Control Flow

The constructor initializes the singleton manager from `good.xml`. Tests check invalid cost levels, valid max level and costs, failure when the schema path is invalid, and completion of partial paths by adding default rack/nodegroup components.

## State And Persistence

State lives in the singleton manager and in-memory configuration. There is no persistence.

## Dependencies And Integration Points

The test integrates with default rack/nodegroup constants, XML topology fixtures, and SCM configuration parsing.

## Risks

Singleton state means constructor-side initialization is shared across tests. The path-completion assertions are tied to the schema shape in `good.xml`.

## Test Signals

Signals include exceptions for levels 0 and max+1, max level 4, allowed costs 0 or 1, runtime failure for missing schema path, completed default rack/nodegroup paths, and null for an uncompletable datacenter-prefixed path.
