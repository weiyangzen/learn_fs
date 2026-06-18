# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDedicatedDiskSpaceUsageFactory.java

## Purpose

This test verifies config-based creation and parameter generation for `DedicatedDiskSpaceUsageFactory`.

## Important APIs, Types, And Functions

`testCreateViaConfig()` delegates to the shared factory-selection test. `testParams()` uses `DedicatedDiskSpaceUsageFactory.Conf.configKeyForRefreshPeriod`, writes `2m` into `OzoneConfiguration`, and checks returned `SpaceUsageCheckParams`.

## Control Flow

Configuration is populated, the factory is configured, params are requested for a temp dir, and assertions inspect directory, refresh, and source class.

## State And Persistence

State is only in-memory configuration and temp path. The test does not exercise persistence behavior.

## Dependencies And Integration Points

It integrates with `SpaceUsageCheckFactory.create`, `DedicatedDiskSpaceUsageFactory`, `DedicatedDiskSpaceUsage`, and duration parsing through Ozone config.

## Risks

Exact duration parsing and exact source class are guarded, but persistence class is not checked here. Changes in default persistence could slip through this test.

## Test Signals

Signals include configured factory selection, `Duration.ofMinutes(2)`, directory identity, and `DedicatedDiskSpaceUsage` source class.
