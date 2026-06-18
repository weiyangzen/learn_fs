# sources/user-network-fs/samba/source3/libnet/libnet_dssync.c

## Purpose

Provides the common DRSUAPI replication driver for Samba `libnet` DSSync backends. It binds to a DC, resolves the naming context, builds and pages through `DsGetNCChanges`, decrypts replicated secret attributes, and dispatches objects and links to backend callbacks.

## Important APIs, Types, and Functions

Public APIs are `libnet_dssync_init_context` and `libnet_dssync`. Internal control points are `libnet_dssync_bind`, `libnet_dssync_lookup_nc`, `libnet_dssync_build_request`, `libnet_dssync_getncchanges`, and `libnet_dssync_process`. `libnet_dssync_free_context` unbinds the DRS policy handle through the talloc destructor.

## Control Flow

`libnet_dssync` creates a temporary context, binds with `DsBind`, resolves `nc_dn` with `DsCrackNames` if needed, calls backend `startup`, chooses whole-NC or single-object replication, builds request level 8 or 5 based on remote extensions, and loops `DsGetNCChanges` until `more_data` is false. It accepts uncompressed and compressed reply levels 1, 2, 6, and 7, updates high-watermarks, decrypts attributes with the RPC auth session key and RID, calls `process_objects`, optionally calls `process_links`, then passes the new up-to-dateness vector to `finish`.

## State and Persistence Behavior

`dssync_context` stores domain identity, RPC pipe, bind handle, session key, naming context DN, replication mode flags, requested object DNs, remote bind info, output filename, backend private data, callbacks, and messages. This layer persists nothing directly; UTDV and imported data are persisted by backends.

## Dependencies and Integration Points

Depends on RPC pipe clients, generated DRSUAPI client stubs, Samba DRS decryption helpers, and backend ops declared in `libnet_dssync.h`.

## Risks and Test Signals

Risks include secret material in memory, unsupported reply/compression levels, partial backend writes on callback failure, and incorrect UTDV use across full, forced, and single-object replication. Tests should cover bind info lengths, level 5/8 requests, compressed replies, incremental vectors v1/v2, linked attributes, and backend error propagation.
