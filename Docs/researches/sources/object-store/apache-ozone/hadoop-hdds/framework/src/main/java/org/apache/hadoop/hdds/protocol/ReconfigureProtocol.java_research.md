# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/protocol/ReconfigureProtocol.java

## Purpose

`ReconfigureProtocol` is the admin RPC interface used by Ozone tools to trigger and observe runtime configuration reloads.

## Important APIs, Types, and Functions

It defines `getServerName()`, `startReconfigure()`, `getReconfigureStatus()`, and `listReconfigureProperties()`, all marked idempotent and throwing `IOException`.

## Control Flow

The interface is implemented by `ReconfigurationHandler`; PB translators adapt the methods to protobuf RPC calls. Reconfiguration itself is asynchronous.

## State and Persistence Behavior

No protocol state. Implementations report task status and apply updates from configuration files.

## Dependencies and Integration Points

It depends on Hadoop `ReconfigurationTaskStatus` and is exposed for SCM, OM, and datanode through role-specific PB interfaces.

## Risks and Test Signals

Callers must handle an in-progress or never-started status. Tests should verify translator round-trips for start/end times, property changes, errors, and allowed property lists.
