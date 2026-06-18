# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ContainerIDParameters.java

## Purpose
Provides reusable positional/stdin parsing and validation for commands that accept one or more container IDs.

## Important APIs, Types, And Functions
`ContainerIDParameters` extends `ItemsFromStdin`. `setContainerIDs` binds `0..*` parameters. `getValidatedIDs(boolean required)` enforces required input, parses positive longs, reports invalid tokens, and deduplicates while preserving first-seen order through `LinkedHashSet`.

## Control Flow
Commands call `getValidatedIDs`; if no IDs are supplied and stdin was not used, it throws `MissingParameterException`. It accumulates invalid inputs before throwing a picocli `ParameterException`.

## State And Persistence
Input tokens are held in the inherited item list. Nothing is persisted.

## Dependencies And Integration Points
Used by container info, report suppression, and reconcile commands. Depends on `ItemsFromStdin` and picocli command spec.

## Risks And Test Signals
Long parsing rejects non-decimal and overflow values. Required=false callers can receive an empty list. Tests should cover stdin marker behavior, duplicate IDs, zero/negative IDs, mixed valid/invalid inputs, and missing required parameters.
