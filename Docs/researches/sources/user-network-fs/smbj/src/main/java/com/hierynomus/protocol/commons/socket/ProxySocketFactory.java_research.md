# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/socket/ProxySocketFactory.java

## Purpose
SocketFactory implementation that creates sockets through an optional Proxy and applies a configurable connect timeout.

## Important APIs / Types / Functions
Defines class `ProxySocketFactory` in package `com.hierynomus.protocol.commons.socket`. Important methods/functions include `ProxySocketFactory`, `createSocket`, `getHttpProxy`. Important fields include `logger`, `DEFAULT_CONNECT_TIMEOUT`, `proxy`, `connectTimeout`. Source size: 94 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: logger, DEFAULT_CONNECT_TIMEOUT, proxy, connectTimeout. Network/file resources are external integration state and require close-path coverage. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: javax.net.SocketFactory, java.io.IOException, java.net.InetAddress, java.net.InetSocketAddress, java.net.Proxy, java.net.Socket. External dependencies: org.slf4j.Logger, org.slf4j.LoggerFactory.

## Risks and Edge Cases
network timeouts, proxy parsing, and close behavior need integration tests.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
