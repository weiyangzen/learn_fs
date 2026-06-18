# sources/user-network-fs/nfs-ganesha/src/include/nfs4.h

## Purpose

`nfs4.h` is a compact wrapper that pulls in local RPC definitions and the generated NFSv4.1 protocol header. It also defines a local maximum NFSv4 domain length fallback.

## Important APIs, Types, and Functions

The header includes `gsh_rpc.h` before `nfsv41.h` so Ganesha's RPC/GSS compatibility definitions are visible. `NFS4_MAX_DOMAIN_LEN` defaults to 512 when not defined elsewhere.

## Control Flow

There is no executable control flow. Compilation units include this header to access NFSv4 scalar, operation, compound, callback, session, and status types from `nfsv41.h`.

## State and Persistence Behavior

No state is defined. The protocol types it exposes describe NFSv4 client/server state such as stateids, sessions, layouts, delegations, and callbacks in other headers and implementation files.

## Dependencies and Integration Points

It integrates every NFSv4 protocol implementation file with generated protocol definitions, local GSS switch behavior, `nfs_proto_data.h`, callback code, file-handle handling, metrics, and ID mapping.

## Risks and Test Signals

Risks are include-order dependency on `gsh_rpc.h`, generated `nfsv41.h` drift, and mismatched domain length assumptions. Tests should compile NFSv4 units under GSS/no-GSS configurations, validate generated XDR compatibility, and exercise owner/group domains near `NFS4_MAX_DOMAIN_LEN`.
