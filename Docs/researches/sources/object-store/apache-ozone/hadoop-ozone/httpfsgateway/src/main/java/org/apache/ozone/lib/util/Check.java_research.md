# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/Check.java

## Purpose
`Check` provides small argument precondition helpers used throughout the HttpFS support framework.

## Important APIs, types, and functions
`notNull(obj, name)` rejects null values and returns the object. `notEmpty(str, name)` rejects null and empty strings and returns the string.

## Control flow
Each method throws `IllegalArgumentException` with a simple message on validation failure.

## State and persistence behavior
The utility has no state and a private constructor.

## Dependencies and integration points
It is used by `Server`, `BaseService`, `RunnableCallable`, `XException`, `ConfigurationUtils`, `FileSystemAccessService`, and `SchedulerService`.

## Risks and edge cases
`notEmpty` does not trim or reject whitespace-only strings. Callers needing non-blank semantics must add their own checks.

## Test signals
Indirect tests assert null/empty handling in service and rewrite code paths.
