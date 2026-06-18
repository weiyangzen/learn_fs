# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseExpiredException.java

## Purpose

`LeaseExpiredException` reports operations on an already expired/invalidated lease. The complete 45-line source was read for this report.

## Important APIs, Types, and Functions

It extends `LeaseException` with no-argument and message constructors.

## Control Flow

There is no internal flow. `Lease` throws it from time/lifetime/renew methods after invalidation.

## State and Persistence Behavior

It owns no state beyond inherited exception fields.

## Dependencies and Integration Points

It is used by `Lease` and caught by `LeaseManager.LeaseMonitor`.

## Risks and Edge Cases

No cause constructor is provided. Timeout detection itself is handled by `LeaseManager`; `Lease` only knows it was invalidated.

## Test Signals

Tests should verify invalidated leases throw this exception from elapsed/remaining/lifetime/renew methods.
