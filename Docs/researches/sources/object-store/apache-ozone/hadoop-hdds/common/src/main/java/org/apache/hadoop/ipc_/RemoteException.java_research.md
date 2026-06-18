
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RemoteException.java

## Purpose

`RemoteException` represents an exception thrown by a remote RPC server. It preserves the remote exception class name, message, and optional protobuf RPC error code, and can attempt to unwrap the remote type locally.

## Important APIs, types, and functions

Constructors accept class name, message, and optional `RpcErrorCodeProto`. `getClassName()` and `getErrorCode()` expose metadata. `unwrapRemoteException(Class<?>...)` unwraps only matching lookup types. `unwrapRemoteException()` tries to load the remote class as an `IOException` subclass. `instantiateException()` requires a public/string constructor, sets the `RemoteException` as cause, and returns the new exception. `valueOf(Attributes)` builds from XML attributes.

## Control flow

Client-side code receives `RemoteException`, optionally calls unwrap, and either gets a more specific local `IOException` or the original `RemoteException`. Unknown class names, non-IO classes, missing constructors, or unmatched lookup classes all fall back to `this`.

## State and persistence behavior

State is immutable exception metadata plus inherited stack trace. It is not persisted except when serialized/logged by callers.

## Dependencies and integration points

It integrates with protobuf RPC response error codes, XML/SAX conversion, failover code, and Ozone tests such as `TestRemoteEx`, `TestSecretKeysApi`, and HA follower-read tests.

## Risks and test signals

Reflection-based unwrapping is sensitive to class availability and constructors. `getErrorCode()` may return null for unspecified or unknown numeric codes. Tests should cover exact lookup unwrapping, generic unwrapping, missing class, class not extending `IOException`, no string constructor, error-code preservation, and `toString()` formatting.
