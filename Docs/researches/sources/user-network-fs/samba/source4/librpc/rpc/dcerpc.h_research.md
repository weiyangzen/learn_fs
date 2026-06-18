# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.h

## Purpose

`dcerpc.h` is the public source4 DCE/RPC client-side interface header. It defines the visible pipe, connection, and security structures while hiding internals unless `SOURCE4_LIBRPC_INTERNALS` is set, and declares connection, bind, auth, alter-context, endpoint mapping, and secondary-connection APIs.

## Important APIs And Types

`struct dcecli_security` stores auth type/level/context id, temporary auth trailer pointers, GENSEC state, session-key callback, and verification state. `struct dcecli_connection` stores call id, negotiated fragment sizes, flags, security state, event context, IO trigger, packet log dir, dead/free flags, transport stream/queue/read state, server name, pending and queued requests, context id allocation, response size limit, and bind-time features. `struct dcerpc_pipe` stores binding handle, context id, object UUID, abstract and transfer syntaxes, connection pointer, binding, last fault code, per-request timeout, connect-time timeout inhibition flags, and presentation-context verification.

Public functions include `dcerpc_pipe_connect*`, `dcerpc_pipe_init`, SMB open helpers, `dcerpc_bind_auth_none`, `dcerpc_pipe_connect_b*`, `dcerpc_pipe_auth`, `dcerpc_init`, secondary SMB/context/auth helpers, `dcerpc_alter_context`, `dcerpc_bind_auth`, and endpoint mapper helpers.

## Control Flow And State

The header defines the state that `dcerpc.c`, `dcerpc_auth.c`, `dcerpc_connect.c`, and transport-specific files mutate. Without `SOURCE4_LIBRPC_INTERNALS`, internals are wrapped in an `internal` struct to discourage direct external access.

## Dependencies And Integration Points

It includes `data_blob.h`, generated `dcerpc.h`, `libndr.h`, and common RPC definitions. It forward-declares tevent, tstream, credentials, resolve, SMB, ROH, TLS, and socket types to avoid broad public includes.

## Risks

The file explicitly notes that removing public functions or changing signatures requires a shared-library version update. Even fields intended as hidden internals can leak into source4 code compiled with `SOURCE4_LIBRPC_INTERNALS`. Timeout and security state fields are subtle and should be modified only with the owning implementation logic.

## Test Signals

ABI/API tests should compile consumers with and without `SOURCE4_LIBRPC_INTERNALS`, verify exported symbols and signatures, and exercise public connect/auth/bind/alter APIs.
