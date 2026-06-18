# sources/user-network-fs/samba/source3/utils/net_rpc_samsync.c

## Purpose

`net_rpc_samsync.c` implements the `net rpc vampire` passdb and keytab paths that use Active Directory DRS replication to pull account data from a remote domain controller. The file is a thin command adapter around `libnet_dssync`, adding domain checks, option propagation, and command usage output.

## Important APIs, Types, and Functions

`rpc_vampire_usage()` prints the historical command usage. `rpc_vampire_ds_internals()` initializes a `struct dssync_context`, verifies the remote domain SID matches the local global SAM SID, sets `ctx->cli`, `ctx->domain_name`, and `ctx->ops = &libnet_dssync_passdb_ops`, and calls `libnet_dssync()`. `rpc_vampire_passdb()` creates an IPC connection, scans the DC, rejects non-AD DCs, rejects AD passdb import unless `--force` is set, and runs the DRSUAPI command with sealing and TCP. `rpc_vampire_keytab_ds_internals()` configures `libnet_dssync_keytab_ops`, output filename, optional object DN list, full-replication and cleanup options, and optional single-object replication. `rpc_vampire_keytab()` performs the same IPC/DC scan and runs DRSUAPI.

## Control Flow

Both exported commands first validate usage, open an IPC connection with `net_make_ipc_connection()`, and inspect the remote DC with `net_scan_dc()`. They require Active Directory because the actual synchronization path is DRSUAPI-based. The passdb path additionally enforces a safety gate: without `--force`, it prints guidance instead of importing from AD. Once the command reaches the RPC runner, the internal function initializes a dssync context, attaches the active pipe and chosen operation vtable, calls `libnet_dssync()`, prints any error or result messages, frees the context, and returns the dssync status.

## State and Persistence

Persistent effects are delegated to `libnet_dssync` operation tables. The passdb path writes account data to Samba's configured local passdb. The keytab path writes or updates the specified Kerberos keytab file, with options for full replication, cleaning old entries, and single-object replication. This file itself stores no persistent state.

## Dependencies and Integration Points

Dependencies include DRSUAPI and Netlogon NDR headers, `libnet/libnet_dssync.h`, machine SID accessors, and the common `net` connection/DC discovery helpers. It integrates with the broader `net rpc vampire` command family rather than registering a local function table in this file.

## Risks

This code intentionally performs sensitive credential/account replication. The passdb domain SID check prevents importing accounts from a mismatched remote domain, but the keytab path does not perform the same local SID compatibility check because it writes keys rather than passdb records. `rpc_vampire_passdb()` has early `return -1` paths after creating an IPC connection and scanning the DC without local cleanup in this file. Most correctness and security risk resides in the selected `libnet_dssync_*_ops` implementations and transport sealing. Operator misuse is a major risk, especially with `--force`, full replication, cleanup of old keytab entries, or single-object filters.

## Test Signals

Test signals include usage validation, non-AD rejection, AD passdb refusal without `--force`, domain SID mismatch handling, keytab filename requirement, propagation of `--force-full-repl`, `--clean-old-entries`, and single-object options, plus mocked `libnet_dssync` success/error/result message handling.
