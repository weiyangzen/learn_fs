# sources/user-network-fs/samba/source4/ntp_signd/ntp_signd.c

## Purpose

`ntp_signd.c` implements Samba's NTP signing daemon service. It listens on a Unix-domain socket, accepts length-prefixed NTP signing requests, looks up the requested trust account in SAMDB, and returns a signed NTP packet using the account's NT hash.

## Important APIs, Types, and Functions

The service registration entry point is `server_service_ntp_signd_init()`, which registers `ntp_signd_task_init()`. Connection handling uses `ntp_signd_accept()`, `ntp_signd_call_loop()`, `ntp_signd_call_writev_done()`, and `ntp_signd_terminate_connection()`. Packet processing is in `ntp_signd_process()`, with `signing_failure()` creating protocol failure replies. Runtime structs are `struct ntp_signd_server`, `struct ntp_signd_connection`, and `struct ntp_signd_call`.

## Control Flow

Task init creates the strict socket directory, opens SAMDB with `system_session()`, constructs `<ntp_signd_socket_directory>/socket`, and binds a stream service. Accept converts the existing socket to a tstream, creates a send queue, and starts reading 4-byte length-prefixed PDUs. Each call strips the length header, NDR-decodes `sign_request`, rejects unsupported operations or protocol versions with a signing-failure reply, constructs a SID from the domain SID plus `key_id & 0x7fffffff`, searches SAMDB for a user object, verifies it is enabled and a trust account, obtains `unicodePwd`, appends key ID and MD5(NT hash || packet) to the packet, NDR-encodes `signed_reply`, queues the write, and immediately starts the next read.

## State and Persistence Behavior

Persistent data is read from SAMDB but not modified. Per-service state holds the task and SAMDB handle. Per-connection state holds stream, send queue, and owning service pointer. Each request allocates input/output blobs and iovecs under `ntp_signd_call`, freed after write completion.

## Dependencies and Integration Points

It integrates with Samba service/task/stream infrastructure, tstream, generated `ndr_ntp_signd`, SAMDB and DSDB search helpers, auth/system sessions, SID utilities, GnuTLS hash helpers, loadparm socket directory/options, and Unix permissions. The build script links it with `samdb`, NDR, tsocket, GnuTLS helpers, and service infrastructure.

## Risks and Edge Cases

The signing algorithm uses MD5 because it matches the protocol, so callers must not treat it as a general modern signature primitive. Access control relies on Unix socket directory permissions and account-type checks. Unsupported protocol operations return protocol failure replies, while disabled/non-trust accounts return access denied and terminate the connection through the caller loop. The code adjusts `call->in.data` past the header without preserving the original pointer, which is acceptable for request scope but should not be reused for freeing. Long or malformed PDUs depend on tstream framing limits outside this file.

## Test Signals

Tests should cover socket directory creation and permissions, valid trust-account signing, unknown SID, duplicate SID search results, disabled account, non-trust account, missing `unicodePwd`, unsupported op/version, malformed NDR, multiple requests on one connection, write failure termination, and exact signed packet layout including key ID and 16-byte digest.
