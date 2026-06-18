# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/DeleteBlockResult.java

## Purpose

`DeleteBlockResult` is a simple holder for SCM block deletion outcomes.

## Important APIs, Types, and Functions

The constructor stores a `BlockID` and `DeleteScmBlockResult.Result`. Accessors are `getBlockID()` and `getResult()`.

## Control Flow

No behavior beyond construction and getters.

## State and Persistence Behavior

State is in-memory mutable fields set by constructor. There is no persistence or protobuf conversion here.

## Dependencies and Integration Points

It depends on HDDS `BlockID` and SCM block-location deletion result protobuf enum. It is consumed by deletion/reporting code that needs to correlate blocks with result statuses.

## Risks and Test Signals

Fields are not final, though there are no setters. Tests should verify constructor/getter mapping and null handling expectations in consumers.
