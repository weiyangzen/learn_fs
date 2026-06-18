# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeActionHdds.java

## Purpose

`UpgradeActionHdds` is a runtime annotation for classes that implement HDDS upgrade finalization actions for SCM or datanode components. The complete 46-line source was read for this report.

## Important APIs, Types, and Functions

Annotation members are `HDDSLayoutFeature feature()` and `Component component()`. Nested enum `Component` has `SCM` and `DATANODE`.

## Control Flow

There is no executable flow. Runtime reflection can discover annotated action classes and match them to layout features/components.

## State and Persistence Behavior

The annotation stores metadata in class files at runtime retention. It does not persist service state.

## Dependencies and Integration Points

It depends on `HDDSLayoutFeature` and Java annotation metadata. Upgrade action discovery/registration code consumes it.

## Risks and Edge Cases

Wrong feature or component annotation can run an action in the wrong service or skip it. Runtime retention makes reflection scanning necessary and testable.

## Test Signals

Tests should verify annotated action discovery, feature/component matching, and rejection or absence handling for misannotated classes.
