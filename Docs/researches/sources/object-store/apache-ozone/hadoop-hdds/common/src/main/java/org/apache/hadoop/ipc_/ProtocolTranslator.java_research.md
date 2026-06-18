
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtocolTranslator.java

## Purpose

`ProtocolTranslator` marks client-side translator classes that wrap an underlying RPC proxy. It lets common RPC utilities reach the real proxy when the public client object is an adapter.

## Important APIs, types, and functions

`getUnderlyingProxyObject()` returns the wrapped proxy object.

## Control flow

`RPC.getConnectionIdForProxy()` checks this interface and unwraps before reading the proxy's invocation handler.

## State and persistence behavior

The interface owns no state. Implementations hold the underlying proxy.

## Dependencies and integration points

It integrates translator/adaptor layers with generic RPC utilities such as connection ID lookup and proxy shutdown.

## Risks and test signals

Returning the wrong object breaks diagnostics and connection handling. Tests should cover translated and non-translated proxies, nested translators if used, and behavior when the underlying proxy is already closed.
