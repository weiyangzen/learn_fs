# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/AbstractDataStreamOutput.java

Purpose: Base class for datastream output implementations that need common retry/error handling.

Important APIs/types/functions: Extends `ByteBufferOutputStream`. Stores retry policy map, retry count, and exception flag. `checkForRetryFailure` identifies Ratis retry/closed failures. `checkIfContainerToExclude` identifies `StorageContainerException`. `handleRetry` selects a retry policy using `HddsClientUtils.checkForException` and enforces sleep/fail behavior. `setExceptionAndThrow` marks the stream exceptional and throws.

Control flow: On retryable IOExceptions, subclasses call `handleRetry`; it asks the selected Hadoop `RetryPolicy` whether to retry or fail. Failures are wrapped as IOExceptions and mark the stream as exceptional. Retry decisions with delay sleep the current thread, handling interruption by re-interrupting and throwing `InterruptedIOException`.

State and persistence behavior: Per-stream in-memory retry count and exception flag. No persistence.

Dependencies and integration points: Used by concrete Ozone datastream outputs. Integrates with Hadoop retry APIs, Ratis exceptions, and storage container exceptions.

Risks: Retry count is shared for all exception types unless subclasses reset it. If `HddsClientUtils.checkForException(exception)` returns a cause class not present in the map, it falls back to generic `Exception`. Thread interruption converts to permanent exception state.

Test signals: Tests should cover retry success with and without delay, fail decisions, interruption, exception classification, and retry-count reset.
