# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAUtils.java

## Purpose

This test verifies that `SCMHAUtils.removeSelfId` removes the current SCM node ID from HA node lists in configuration.

## Important APIs, Types, And Functions

It uses `OZONE_SCM_SERVICE_IDS_KEY`, `OZONE_SCM_NODES_KEY`, `OZONE_SCM_NODE_ID_KEY`, `SCMHAUtils.removeSelfId`, and `HddsUtils.getSCMNodeIds`.

## Control Flow

The test constructs a config with service `mySCM`, nodes `scm1,scm2,scm3`, and self ID `scm3`, calls `removeSelfId`, then reads the resulting node list.

## State And Persistence

State is an in-memory `OzoneConfiguration`. No persistent HA metadata is modified.

## Dependencies And Integration Points

It integrates SCM HA config keys, HDDS config parsing, and utility behavior used when excluding the local SCM from peer operations.

## Risks

The test covers one service and one self ID only. Multi-service configs, whitespace variations, and absent IDs rely on other coverage.

## Test Signals

Signals are exactly two remaining nodes and absence of the self ID.
