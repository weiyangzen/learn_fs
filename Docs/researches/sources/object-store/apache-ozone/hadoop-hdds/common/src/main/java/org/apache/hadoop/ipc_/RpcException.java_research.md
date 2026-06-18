
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcException.java

## Purpose

`RpcException` is the base checked exception for RPC-layer failures that are more specific than plain `IOException`.

## Important APIs, types, and functions

It extends `IOException` and provides package-private constructors for message and message-with-cause.

## Control flow

Subclasses such as `RpcServerException`, `RpcClientException`, `RpcNoSuchMethodException`, and `RpcNoSuchProtocolException` use it to participate in checked exception handling.

## State and persistence behavior

Only inherited exception state is stored.

## Dependencies and integration points

It is the root of the package's typed RPC exception hierarchy and integrates with protobuf response status mapping through subclasses.

## Risks and test signals

The constructors are not public, which keeps external code on defined subclasses. Tests should verify subclass message/cause preservation and serialization compatibility through `serialVersionUID`.
