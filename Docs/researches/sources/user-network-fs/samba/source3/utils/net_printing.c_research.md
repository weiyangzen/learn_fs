# sources/user-network-fs/samba/source3/utils/net_printing.c

## Purpose
This file implements `net printing`, a local and RPC-assisted utility for inspecting old printing TDB databases and migrating their forms, drivers, printers, and security descriptors into registry-backed storage.

## Important APIs, Types, And Control Flow
`struct printing_opts` stores optional input encoding and TDB path. `printing_parse_args()` treats `encoding=<CP>` specially and the remaining argument as the TDB file. `net_printing_dump()` opens the TDB read-only, optionally overrides `dos charset`, traverses keys by prefix (`FORMS/`, `DRIVERS/`, `PRINTERS/`, `SECDESC/`), decodes values through generated NDR pull functions, and prints NDR structures. `printing_migrate_internal()` follows a similar traversal but calls `printing_tdb_migrate_form()`, `printing_tdb_migrate_driver()`, `printing_tdb_migrate_printer()`, and in a second pass `printing_tdb_migrate_secdesc()`. `net_printing_migrate()` runs that internal function through `run_rpc_command()` bound to the winreg interface. `net_printing()` dispatches `dump` and `migrate`.

## State And Persistence
Dump mode is read-only except for temporary charset override restored at exit. Migrate mode reads the legacy TDB and writes through a remote/local winreg RPC pipe into the new printing registry storage. TDB record buffers are manually freed with `SAFE_FREE()`.

## Dependencies And Integration Points
Dependencies include TDB, generated NDR for ntprinting/spoolss/security/winreg, RPC client helpers, Samba charset configuration, and `printing/nt_printing_migrate.h`. The migration command integrates with the broader RPC connection machinery via `run_rpc_command()`.

## Risks And Test Signals
Argument parsing silently lets later non-encoding args replace the TDB path. Charset override must always be restored, including error paths. Prefix-based traversal ignores unknown records. Migration intentionally processes security descriptors after objects, so ordering tests matter. Test dump of each prefix, corrupted NDR blobs, encoding conversion, missing TDB, multiple non-option args, RPC connection failure, and successful migration ordering.
