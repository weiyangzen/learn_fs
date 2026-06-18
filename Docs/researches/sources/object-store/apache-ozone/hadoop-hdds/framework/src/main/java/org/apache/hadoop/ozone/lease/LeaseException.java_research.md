# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseException.java

## Purpose

`LeaseException` is the checked base exception for lease-specific failures. The complete 45-line source was read for this report.

## Important APIs, Types, and Functions

It extends `Exception` and provides no-argument and message constructors.

## Control Flow

There is no internal control flow.

## State and Persistence Behavior

It owns no state beyond inherited exception fields.

## Dependencies and Integration Points

It is the base for `LeaseAlreadyExistException`, `LeaseExpiredException`, and `LeaseNotFoundException`.

## Risks and Edge Cases

No cause constructor is provided.

## Test Signals

Direct tests can verify checked-exception hierarchy and messages; most coverage is through `LeaseManager`.
