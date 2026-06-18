
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcClientException.java

## Purpose

`RpcClientException` represents RPC client-side failures within the IPC exception hierarchy.

## Important APIs, types, and functions

It extends `RpcException` and has package-private constructors for message-only and message-with-cause forms.

## Control flow

IPC client internals can throw this subtype when failures are attributable to the client side rather than server response status.

## State and persistence behavior

Only inherited exception state is stored.

## Dependencies and integration points

It integrates with `RpcException` and checked `IOException` handling inside the IPC client package.

## Risks and test signals

Because constructors are package-private, external code cannot create it directly. Tests in the package should cover message/cause propagation and classification distinct from `RpcServerException`.
