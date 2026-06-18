# sources/user-network-fs/libsmb2/lib/init.c

## Purpose
`init.c` owns libsmb2 context creation, destruction, URL parsing, error storage, credential setters, active-context tracking, I/O vector helpers, and miscellaneous context configuration APIs. It is the lifecycle and configuration entry point for most client-side libsmb2 users.

## Important APIs, Types, and Functions
Key public functions include `smb2_parse_url()`, `smb2_destroy_url()`, `smb2_init_context()`, `smb2_destroy_context()`, `smb2_active_contexts()`, `smb2_context_active()`, `smb2_free_iovector()`, `smb2_add_iovector()`, `smb2_set_error()`, `smb2_set_nterror()`, `smb2_get_error()`, `smb2_get_nterror()`, `smb2_set_client_guid()`, credential setters/getters, security/sign/seal/version/timeout setters, passthrough and oplock callback setters, and `smb2_delegate_credentials()`. The private parser `smb2_parse_args()` handles URL query arguments.

## Control Flow
`smb2_parse_url()` validates the `smb://` prefix and maximum URL size, parses query arguments, then splits optional `domain;user@server/share/path` components into an allocated `smb2_url`. `smb2_parse_args()` mutates the query string in place, recognizes `seal`, `sign`, `ndr3264`, `ndr32`, `ndr64`, endian flags, `sec=krb5|krb5cc|ntlmssp`, dialect `vers=...`, and `timeout=...`, and rejects incompatible `seal` use with non-SMB3 dialects. `smb2_init_context()` seeds pseudo-random client challenge/salt/guid data, defaults the user from `getlogin_r()` or `Guest`, initializes transport and negotiation defaults, and links the context into the global active list. `smb2_destroy_context()` closes sockets, cancels queued/current/waiting PDUs with shutdown/cancel statuses, frees buffers and credentials, releases optional GSS credentials, unlinks the context, and frees it. Setter functions replace owned strings with `strdup()` copies and trigger password-file lookup where relevant.

## State and Persistence Behavior
The file maintains a process-global `active_contexts` singly linked list. Each `smb2_context` owns socket descriptors, connecting file descriptors, queued PDUs, input vectors, error strings, NT status, session keys, encryption state, credentials, callbacks, and optional delegated GSS credentials. `smb2_set_password_from_file()` reads the `NTLM_USER_FILE` environment variable and loads a matching `domain:user:password` line, using empty-domain entries as defaults. No repository files are written, but credentials can be loaded from an external user file and retained in the context.

## Dependencies and Integration Points
It depends on `libsmb2.h`, `libsmb2-private.h`, `smb2.h`, `slist.h`, `compat.h`, socket/time/errno/unistd headers, and optional GSS/Kerberos symbols behind `HAVE_LIBKRB5`. Other libsmb2 modules rely on this file for context allocation, cleanup callbacks, error reporting, URL parsing, authentication mode selection, and pass-through credential delegation.

## Risks and Edge Cases
`smb2_parse_url()` leaks the allocated `smb2_url` if it fails after allocation because some error paths return NULL without calling `smb2_destroy_url()`. Query parsing writes NUL bytes into the local URL copy and assumes options with required values actually have `value`; malformed `sec`, `vers`, or `timeout` arguments without `=` can lead to NULL dereferences. `smb2_get_libsmb2Version()` assigns `patch_version` from `LIBSMB2_MAJOR_VERSION`, which looks suspicious. Random material is generated with `srandom/random`, suitable for protocol nonces only if the broader library accepts that strength. The global active list is not synchronized, so multi-threaded context create/destroy/enumerate needs external discipline.

## Test Signals
Tests should cover valid and invalid URL forms, query combinations, seal with SMB2 rejection and SMB3 acceptance, credential file matching by domain/server/default, setter replacement/free behavior, destroy callbacks for outqueue/current/waitqueue PDUs, active-list membership before and after destroy, iovector capacity overflow cleanup, error callback invocation, and Kerberos credential delegation when compiled with and without `HAVE_LIBKRB5`.
