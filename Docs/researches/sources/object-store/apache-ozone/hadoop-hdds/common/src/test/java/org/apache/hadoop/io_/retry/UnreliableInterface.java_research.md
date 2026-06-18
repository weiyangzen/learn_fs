# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/UnreliableInterface.java

## Purpose
Defines the retry-test contract implemented by `UnreliableImplementation`.

## Important APIs, types, and functions
- Declares methods that always succeed, always fail fatally, fail once, fail ten times, and fail with SASL or access-control exceptions.
- Defines nested exception types `UnreliableException` and `FatalException`.
- Uses Hadoop retry annotations such as `@Idempotent` where relevant and imports retry interfaces.

## Control flow
As an interface, it has no implementation control flow beyond method signatures and exception contracts.

## State and persistence behavior
No state or persistence in the interface.

## Dependencies and integration points
Used by `RetryProxy` tests to generate dynamic proxies with known method exception signatures and idempotency metadata.

## Risks and test signals
The interface is a fixture contract; changing signatures or annotations changes what retry proxy behavior is exercised.
