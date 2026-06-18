# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseAlreadyExistException.java

## Purpose

`LeaseAlreadyExistException` reports an attempt to acquire a lease for a resource that already has one. The complete 46-line source was read for this report.

## Important APIs, Types, and Functions

It extends `LeaseException` with no-argument and message constructors.

## Control Flow

There is no internal control flow. `LeaseManager.acquire` throws it when `activeLeases` already contains the resource.

## State and Persistence Behavior

It has no state beyond exception message.

## Dependencies and Integration Points

It depends on `LeaseException` and is part of `LeaseManager` acquire API.

## Risks and Edge Cases

No cause constructor is provided.

## Test Signals

Tests should verify duplicate acquisition throws this checked exception with the resource message.
