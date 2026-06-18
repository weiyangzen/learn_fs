# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslRpcServer.java

## Purpose

`SaslRpcServer` encapsulates server-side SASL setup for the forked Hadoop IPC layer. It maps Hadoop `AuthMethod` values to configured SASL mechanisms, creates SASL servers for token and Kerberos modes, and provides token encoding/decoding and callback handlers.

## APIs and control flow

Construction records auth method, mechanism, protocol, and server ID. SIMPLE returns without SASL setup; TOKEN uses an empty protocol and default realm; KERBEROS parses the current user's service principal. `create(connection, saslProperties, secretManager)` builds a token or Kerberos callback handler, optionally runs creation as the current UGI, and errors if no `SaslServer` implementation exists. `init` installs the PLAIN security provider and builds a cached `FastSaslServerFactory`. Token helpers base64-encode identifiers and passwords and reconstruct token identifiers from serialized bytes.

## State, dependencies, and integration

Static state is the cached `SaslServerFactory`. Instance state describes the selected auth method and SASL service identity. Dependencies include Hadoop UGI, token `SecretManager`, forked IPC server connection, Hadoop `SaslPlainServer`, local customized callbacks, Java SASL APIs, and Commons Base64. It integrates with RPC server connection authentication.

## Risks and test signals

`init` must run before `create`, or `saslFactory` is null. Kerberos construction assumes principal parsing by splitting on `/` and `@`. The digest callback sets `connection.attemptingUser` before authorization completes, so caller handling must treat it carefully. Tests should cover factory initialization, token password lookup, invalid token deserialization, authorization ID mismatch, customized unknown callbacks, Kerberos missing host part, and mechanism cache contents.
