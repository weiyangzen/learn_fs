# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/TestSecurityConfigTlsSettings.java

## Purpose
Tests TLS protocol and cipher-suite parsing in `SecurityConfig`.

## Important APIs, types, and functions
- Uses `OzoneConfiguration` and `SecurityConfig`.
- Covers default protocols, single/multiple protocol values, whitespace trimming, empty protocol values, default ciphers, and multiple ciphers.

## Control flow
Each test sets relevant security configuration keys, constructs `SecurityConfig`, and asserts the returned protocol or cipher arrays/lists match expected values.

## State and persistence behavior
Configuration is in-memory. No keystores or certificates are persisted.

## Dependencies and integration points
`SecurityConfig` feeds TLS setup for Ozone/HDDS services and clients.

## Risks and test signals
Parsing errors can disable protocols unexpectedly or include malformed cipher names. These tests signal safe defaults and correct comma-separated value handling.
