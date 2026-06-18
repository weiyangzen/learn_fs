# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/Lease.java

## Purpose

`Lease<T>` represents a timed lease over a resource with optional expiration callback. The complete 189-line source was read for this report.

## Important APIs, Types, and Functions

Important methods are constructors, `hasExpired`, `getElapsedTime`, `getRemainingTime`, `getLeaseLifeTime`, `renew`, `equals`, `hashCode`, `toString`, package-private `getCallback`, `invalidate`, and static `messageForResource`.

## Control Flow

Construction stores resource, creation time from `Time.monotonicNow`, atomic timeout, optional callback, and non-expired state. Accessors throw `LeaseExpiredException` after invalidation. `renew` adds to the timeout atomically. Equality and hash code are based solely on resource.

## State and Persistence Behavior

State is in-memory only: resource, creation time, timeout, expired flag, and callback. There is no persistence.

## Dependencies and Integration Points

It depends on Hadoop `Time`, `Callable`, `AtomicLong`, and lease exception classes. `LeaseManager` creates, renews, invalidates, and monitors leases.

## Risks and Edge Cases

The `expired` flag is not volatile, though manager operations are partly synchronized and monitor reads may be concurrent. `renew` adds a delta rather than replacing expiration. Callback is nulled on invalidation. Resource equality must be stable.

## Test Signals

Tests should cover remaining/elapsed time, renew semantics, expired exceptions after invalidation, equality by resource, and callback clearing.
