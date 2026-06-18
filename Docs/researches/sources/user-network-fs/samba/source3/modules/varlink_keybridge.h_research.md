<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/varlink_keybridge.h -->
# sources/user-network-fs/samba/source3/modules/varlink_keybridge.h

## Purpose
This header defines the public interface for the varlink keybridge client. It describes how Samba requests scoped configuration or key entries and how returned data is represented.

## Important APIs, Types, And Functions
`enum varlink_keybridge_kind` distinguishes default, base64 binary, and UTF-8/plain value data. `enum varlink_keybridge_status` distinguishes connection/protocol failure, successful result, and server-returned error. `struct varlink_keybridge_config` carries socket path, scope, entry name, and desired kind. `struct varlink_keybridge_result` carries status, actual kind, and result or error data. `varlink_keybridge_entry_get` performs the request and allocates a result from the supplied memory context.

## Control Flow
The header has no runtime flow, but its contract is request/response oriented: callers populate config, pass an output pointer, and inspect both the boolean return value and result status when populated.

## State And Persistence
The header stores no state. It documents talloc ownership of returned result data and leaves persistence to the external keybridge service.

## Dependencies And Integration Points
It requires Samba core types such as `TALLOC_CTX` and is included by consumers that need local secret/config lookup. Its comments explicitly connect the API to encrypted CephFS share setup and local varlink-mediated secret retrieval.

## Risks
The boolean return and `status` enum are distinct; callers must not assume a populated result on all false returns. The `char *` fields are mutable pointers, so callers should preserve storage for config values through the call.

## Test Signals
Compile-time coverage should confirm enum and struct use across consumers. Runtime validation belongs to `varlink_keybridge.c` tests with successful, error, and failed connection paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/varlink_keybridge.h -->
