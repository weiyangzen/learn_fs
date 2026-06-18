# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutVersionManagerMXBean.java

## Purpose

`LayoutVersionManagerMXBean` exposes layout version manager values over JMX. The complete 27-line source was read for this report.

## Important APIs, Types, and Functions

It declares `getMetadataLayoutVersion` and `getSoftwareLayoutVersion`.

## Control Flow

There is no implementation flow. `AbstractLayoutVersionManager` implements it and registers an MBean.

## State and Persistence Behavior

The interface owns no state. Implementations expose in-memory layout version values derived from persistent metadata and software feature definitions.

## Dependencies and Integration Points

It integrates with Hadoop `MBeans` registration in `AbstractLayoutVersionManager`.

## Risks and Edge Cases

JMX consumers rely on stable method names. Exposing only versions omits upgrade state, so monitoring must combine with other signals if needed.

## Test Signals

Tests should verify MBean registration exposes both attributes and unregisters on close.
