<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/ExecutionUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/ExecutionUtil.java

## Purpose

`ExecutionUtil` is a small utility for running a checked action once and, if it fails, running cleanup while rethrowing the original exception.

## Important APIs, Types, and Functions

The API is `create(CheckedRunnable)`, `onException(CheckedRunnable)`, and `execute`. It is generic over exception type `E extends Throwable`.

## Control Flow

`execute` is guarded by a `completed` flag so the try block runs at most once. If the try block throws, it runs the registered cleanup block, logs cleanup failures, and rethrows the original exception.

## State and Persistence Behavior

State is in-memory: the try runnable, cleanup runnable, and volatile completion flag. No persistence occurs.

## Dependencies and Integration Points

It uses Ratis `CheckedRunnable` and SLF4J. It is useful around HA operations that need best-effort rollback without masking the root failure.

## Risks and Edge Cases

If `onException` is not set and the try block fails, `execute` will throw a null-pointer while attempting cleanup, masking behavior may differ from intent. `completed` prevents retry after a failed first execution.

## Test Signals

Tests should cover success running once, failure invoking cleanup and rethrowing original, cleanup failure logged but not replacing original, and repeated `execute` no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/ExecutionUtil.java -->
