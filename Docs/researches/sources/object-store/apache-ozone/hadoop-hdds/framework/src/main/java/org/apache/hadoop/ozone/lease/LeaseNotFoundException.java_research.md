# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseNotFoundException.java

## Purpose

`LeaseNotFoundException` reports lookup or release of a resource without an active lease. The complete 46-line source was read for this report.

## Important APIs, Types, and Functions

It extends `LeaseException` and provides no-argument and message constructors.

## Control Flow

There is no internal flow. `LeaseManager.get` and `release` throw it when no lease is found.

## State and Persistence Behavior

It owns no state beyond inherited exception fields.

## Dependencies and Integration Points

It is part of the `LeaseManager` get/release API and is caught by the monitor during concurrent expiration/release races.

## Risks and Edge Cases

No cause constructor is provided.

## Test Signals

Tests should verify missing get/release paths and concurrent release/monitor races do not break the monitor.
