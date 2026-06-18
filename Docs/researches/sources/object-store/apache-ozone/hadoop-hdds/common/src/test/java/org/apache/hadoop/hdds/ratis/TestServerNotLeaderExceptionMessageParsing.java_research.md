# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestServerNotLeaderExceptionMessageParsing.java

## Purpose
Tests parsing of Ratis `ServerNotLeaderException` messages so HDDS can extract leader information from known Ratis error text.

## Important APIs, types, and functions
- Exercises `RatisHelper` leader parsing logic for server-not-leader messages.
- Uses JUnit assertions to verify parsed host and port results for sample exception strings.

## Control flow
The test feeds representative exception messages into the parser and asserts the expected leader address is returned. It also covers message variants where leader information may be absent or formatted differently.

## State and persistence behavior
No persistent state is used. The test is pure string parsing.

## Dependencies and integration points
This is an integration guard for HDDS retry/failover behavior that depends on Ratis exception text when a client talks to a non-leader server.

## Risks and test signals
The brittle dependency is Ratis message format. A format change can break leader discovery and client rerouting; this test signals whether known message shapes still parse correctly.
