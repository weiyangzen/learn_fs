# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/SaslRpcClient.java

## Purpose

`SaslRpcClient` encapsulates client-side SASL negotiation for the forked Hadoop IPC package. It supports SIMPLE fallback, token-based DIGEST-style authentication, Kerberos/GSSAPI authentication, principal validation, and optional stream wrapping for integrity/privacy QoP.

## APIs and control flow

Construction records UGI, protocol, server address, configuration, and SASL properties resolver. `saslConnect` sends a NEGOTIATE request, reads SASL RPC packets, handles server ERROR/FATAL responses, selects the first supported auth type, creates a `SaslClient`, evaluates challenges, handles SUCCESS, and returns the negotiated `AuthMethod`. `selectSaslClient` filters advertised auths through `isValidAuthType`, supports SIMPLE without creating a SASL client, and throws `AccessControlException` if no usable auth remains. `createSaslClient` resolves token credentials or validates Kerberos principals before calling `Sasl.createSaslClient`. `getInputStream` and `getOutputStream` wrap streams when negotiated QoP is not `auth`.

## State, dependencies, and integration

State includes `saslClient`, `authMethod`, UGI, protocol, server address, configuration, and resolver. Dependencies include Hadoop security APIs, token selectors, Kerberos annotations, forked IPC protobufs, Ratis/Hadoop RPC helpers, protobuf `ByteString`, RE2/J glob patterns, and the local `SaslMechanismFactory`. It integrates directly with `Client.IpcStreams` and RPC connection setup.

## Risks and test signals

Principal validation is strict unless a `<serverKey>.pattern` override is configured. Wrapped input requires every post-negotiation packet to be SASL WRAP, otherwise it throws. `useWrap()` assumes negotiation completed and `saslClient` exists. Tests should cover SIMPLE negotiation, token selection failure, Kerberos principal mismatch, challenge/response token presence, malformed packet detection, QoP wrapping/unwrapping, disposal, and auth method reporting after failures.
