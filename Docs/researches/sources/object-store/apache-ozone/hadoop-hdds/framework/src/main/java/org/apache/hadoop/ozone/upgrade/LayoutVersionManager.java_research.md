# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutVersionManager.java

## Purpose

`LayoutVersionManager` is the read-only interface for a component's metadata/software layout version and feature availability. The complete 83-line source was read for this report.

## Important APIs, Types, and Functions

Methods are `getMetadataLayoutVersion`, `getSoftwareLayoutVersion`, `needsFinalization`, `isAllowed(LayoutFeature)`, `isAllowed(String)`, `getFeature(String)`, `getFeature(int)`, `unfinalizedFeatures`, default `getHandler`, and `close`.

## Control Flow

The interface has no implementation flow except default `getHandler`, which returns null.

## State and Persistence Behavior

Implementations maintain in-memory layout state and coordinate with persistent VERSION metadata externally.

## Dependencies and Integration Points

It depends on `LayoutFeature` and is implemented by `AbstractLayoutVersionManager`. Services query it to guard feature use before finalization.

## Risks and Edge Cases

Callers must handle null from `getFeature` or default `getHandler`. `isAllowed` is the primary compatibility gate and must be used consistently.

## Test Signals

Tests should exercise component implementations for feature gating, unfinalized feature ordering, handler overrides, and close lifecycle.
