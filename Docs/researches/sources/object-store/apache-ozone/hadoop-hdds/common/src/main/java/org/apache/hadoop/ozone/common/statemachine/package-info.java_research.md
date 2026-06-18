# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/statemachine/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone.common.statemachine` as a template state-machine package for Ozone.

## APIs and integration

It has no runtime API. It groups `StateMachine` and `InvalidStateTransitionException`, which provide a generic enum transition table and typed invalid-transition failure.

## State, dependencies, risks, and test signals

The file has no state or persistence behavior. The only risk is stale documentation if the package expands beyond a generic state-machine template. Compilation and JavaDoc generation are sufficient test signals.
