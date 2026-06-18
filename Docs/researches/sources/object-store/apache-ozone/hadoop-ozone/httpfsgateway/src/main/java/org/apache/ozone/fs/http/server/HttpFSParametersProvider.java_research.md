# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/HttpFSParametersProvider.java

## Purpose
`HttpFSParametersProvider` defines the typed query-parameter schema for every HttpFS operation and plugs it into the shared WSRS `ParametersProvider`.

## Important APIs, Types, and Functions
`PARAMS_DEF` maps each `HttpFSConstants.Operation` to the parameter classes allowed for that operation. Nested parameter types extend `BooleanParam`, `LongParam`, `ShortParam`, `StringParam`, `EnumParam`, and `EnumSetParam`. Important parameters include offset/length, data/noredirect, recursive, filter, owner/group, permission/unmasked permission, ACL spec, replication, sources/destination, xattr fields, storage policy, snapshot names, fsaction, and EC policy.

## Control Flow
`HttpFSServer` calls `PARAMETERS_PROVIDER.get(request)` to parse request parameters. The provider uses the `op` parameter to pick allowed parameter classes and instantiate typed values with defaults and optional validation patterns.

## State and Persistence Behavior
The class holds static parameter definitions only. It does not persist runtime state.

## Dependencies and Integration Points
It must stay synchronized with `HttpFSConstants.Operation` and the switch handlers in `HttpFSServer`. `AclPermissionParam` dynamically reads the ACL permission regex from `HttpFSServerWebApp`'s `FileSystemAccess` configuration.

## Risks and Edge Cases
Parameter defaults affect behavior: overwrite defaults true, offset defaults zero, length/blocksize/replication/time defaults use sentinel values. `FsActionParam` has a validating constructor, but the no-arg constructor passes null without a pattern. XAttr names are limited to user/trusted/system/security namespaces. Operations can be declared here even if the server rejects them as unsupported.

## Test Signals
No direct tests in this subset. Good coverage would validate parsing defaults, invalid enum values, ACL/xattr patterns, repeated xattr names, and operation-to-parameter alignment.
