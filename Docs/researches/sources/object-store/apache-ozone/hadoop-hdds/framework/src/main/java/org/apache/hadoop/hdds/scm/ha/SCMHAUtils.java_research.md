# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAUtils.java

## Purpose

`SCMHAUtils` centralizes utility logic for SCM high availability: primordial-node detection, Ratis directory selection, node-list manipulation, exception unwrapping/classification, and retry/failover decisions.

## Important APIs, Types, and Functions

Key methods include `getPrimordialSCM`, `isPrimordialSCM`, `getSCMRatisDirectory`, `getSCMRatisSnapshotDirectory`, `removeSelfId`, `unwrapException`, exception classifiers, and `getRetryAction`.

## Control Flow

Directory methods use explicit config values or fall back to component defaults. `removeSelfId` clones configuration, removes the local SCM ID from service-specific node lists, and returns the clone. Retry action first fails for access-control and no-failover RPC exceptions, retries without failover for specific retriable classes, fails for known non-retriable SCM exceptions, and otherwise failovers until max count.

## State and Persistence Behavior

The class is stateless. Returned configurations/directories affect external HA/Ratis persistence.

## Dependencies and Integration Points

It depends on SCM config keys, `HddsUtils`, Ratis exceptions, Hadoop retry policies, remote exceptions, and SCM-specific exception classes.

## Risks and Test Signals

Exception classification depends on wrapping shapes and class lists. `removeSelfId` does not trim node IDs. Tests should cover direct/wrapped exceptions, access-control failure, retry count boundaries, directory fallbacks, and node-list removal.
