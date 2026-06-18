# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseManagerNotRunningException.java

## Purpose

`LeaseManagerNotRunningException` reports lease manager API calls made before start or after shutdown. The complete 45-line source was read for this report.

## Important APIs, Types, and Functions

It extends `RuntimeException` and provides no-argument and message constructors.

## Control Flow

There is no internal control flow. `LeaseManager.checkStatus` throws it when `isRunning` is false.

## State and Persistence Behavior

It owns no state beyond inherited exception fields.

## Dependencies and Integration Points

It is used by `LeaseManager` public APIs except `start`.

## Risks and Edge Cases

It is unchecked, unlike most other lease exceptions. No cause constructor is provided.

## Test Signals

Tests should verify manager methods throw it before `start` and after `shutdown`, including repeated shutdown.
