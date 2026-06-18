# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/LambdaTestUtils.java

Purpose: `LambdaTestUtils` provides Java-lambda-friendly retry and await utilities for tests, modeled after Hadoop wait helpers and ScalaTest-style await behavior.

Important APIs and types: Main APIs are `await(int, Callable<Boolean>, Callable<Integer>, TimeoutHandler)`, `await(int, int, Callable<Boolean>)`, `TimeoutHandler`, `GenerateTimeout`, `FixedRetryInterval`, `FailFastException`, and `VoidCallable`. It uses Hadoop `Time.monotonicNow` and SLF4J logging.

Control flow: `await` computes an end time, repeatedly invokes the check callable, returns the iteration count on success, stores non-fatal throwables for timeout diagnostics, rethrows `InterruptedException`, `FailFastException`, and `VirtualMachineError` immediately, and sleeps according to the retry callable while time remains. On timeout it invokes the timeout handler, falls back to `GenerateTimeout` if the handler returns null, then rethrows the resulting throwable as exception or error.

State and persistence behavior: No persistence. Runtime state includes iteration count, last caught throwable, retry invocation count in `FixedRetryInterval`, and timeout messages.

Dependencies and integration points: Used by asynchronous tests that need custom retry intervals, fail-fast aborts, or richer timeout exception handling than a simple polling loop.

Risks: A negative retry interval ends polling early. Timeout handlers can throw or return unexpected throwable types; `raise` casts non-Exception throwables to `Error`. The utility logs repeated failures only at debug level.

Test signals: Downstream tests can assert iteration counts, generated `TimeoutException` messages, retry invocation counts, and fail-fast behavior.
