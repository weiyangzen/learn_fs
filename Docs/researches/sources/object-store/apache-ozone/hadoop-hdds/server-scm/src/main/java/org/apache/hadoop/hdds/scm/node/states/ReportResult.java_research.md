# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/ReportResult.java

## Purpose
`ReportResult<T>` is a generic immutable-style result describing reconciliation between a datanode report and SCM's node-to-object mappings, such as missing and newly discovered containers or pipelines.

## Important APIs, Types, And Functions
It stores `ReportStatus`, `missingEntries`, and `newEntries`. Getters expose those fields. `ReportResultBuilder<T>` sets status, missing entries, and new entries, defaulting omitted sets to `Collections.emptySet()` during `build`. `ReportStatus` covers all-well, missing, new, combined missing/new, and new-datanode cases.

## Control Flow
The builder normalizes null missing/new sets to empty sets before constructing the result. The private constructor enforces non-null sets with `Objects.requireNonNull`.

## State And Persistence Behavior
The class holds references to the sets passed to the builder or singleton empty sets. It has no durable persistence. Fields are private but not final, though there are no setters on the built object.

## Dependencies And Integration Points
It is generic and only depends on Java collections. It is intended for node report reconciliation components that compare SCM state with datanode-reported state.

## Risks And Edge Cases
The builder does not require a status, so a result with null status is possible. Provided sets are not defensively copied, so external mutation can alter the result. Consumers must interpret `NEW_DATANODE_FOUND` separately from normal new-entry reconciliation.

## Test Signals
Tests should verify null-set normalization, status coverage, set preservation, and caller behavior for missing status or externally mutated input sets.
