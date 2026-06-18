
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ProtoUtil.java

## Purpose

`ProtoUtil` centralizes protobuf conversions for IPC connection context and request headers. It bridges Java RPC/security state into generated protobuf messages.

## Important APIs, types, and functions

`makeIpcConnectionContext()` builds `IpcConnectionContextProto` with protocol and user information based on `AuthMethod`. `getUgi()` reconstructs `UserGroupInformation` from connection context or user info. `convert()` maps between `RPC.RpcKind` and `RpcKindProto`. `makeRpcRequestHeader()` builds `RpcRequestHeaderProto` with kind, operation, call ID, retry count, client ID, optional `CallerContext`, and optional `AlignmentContext` state.

## Control flow

For Kerberos, the connection context sends only effective user because real user comes from authentication. For token auth, no user fields are sent. For simple auth, effective and optional real users are included. Request header creation always sets core fields, then conditionally attaches caller context and alignment information.

## State and persistence behavior

The class is static and stateless. It creates protobuf messages for network transmission but stores nothing locally.

## Dependencies and integration points

It depends on generated IPC protobuf classes, `SaslRpcServer.AuthMethod`, `UserGroupInformation`, `CallerContext`, `AlignmentContext`, and `RPC.RpcKind`. It is used by client connection setup and per-call request framing.

## Risks and test signals

Security semantics are sensitive to auth method: leaking real users for token/Kerberos or omitting users for simple auth would break impersonation. Tests should cover each auth method, proxy-user reconstruction, unknown enum conversions returning null, caller-context signatures, alignment context mutation, and UUID/client ID byte preservation.
