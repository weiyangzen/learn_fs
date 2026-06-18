# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/ha/TestOzoneNetUtils.java

## Purpose
Tests Ozone network utility behavior for preserving host names in socket addresses.

## Important APIs, types, and functions
- Uses `OzoneNetUtils.getAddressWithHostName`, Hadoop `NetUtils`, and `InetSocketAddress`.
- Test case is `testGetAddressWithHostName`.

## Control flow
The test creates or parses a socket address, passes it through Ozone net utility code, and asserts the resulting address retains the expected host name rather than only resolved address data.

## State and persistence behavior
No persistent state; only socket address objects are used.

## Dependencies and integration points
HA and service discovery code often needs configured hostnames preserved for certificates, RPC, or advertised addresses.

## Risks and test signals
Premature DNS resolution or lost hostnames can break HA routing and TLS hostname checks. This test signals hostname-preserving address handling.
