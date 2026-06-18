# sources/user-network-fs/samba/source3/printing/nt_printing_migrate_internal.c

Purpose: orchestrates one-time migration from legacy print TDB files into the current registry-backed print store, then renames successfully processed TDB files to `.bak`.

Important APIs and functions: `nt_printing_tdb_migrate()` is the exported entry point. It locates `ntdrivers.tdb`, `ntprinters.tdb`, and `ntforms.tdb`, opens an internal winreg pipe as the system session, and calls `migrate_internal()` for each existing file. `migrate_internal()` opens a TDB read-only, walks records by prefix (`FORMS/`, `DRIVERS/`, `PRINTERS/`, `SECDESC/`), calls the conversion functions in `nt_printing_migrate.c`, and handles security descriptors in a second pass. `rename_file_with_suffix()` moves migrated databases to `*.bak`, treating `ENOENT` as non-fatal.

Control flow: migration first handles forms, drivers, and printers so target printer objects exist before security descriptors are applied. Secdesc failures for missing printers are skipped; other failures abort the file migration. If no legacy databases exist, migration succeeds without opening winreg.

State and persistence: reads legacy state from `state_path()` TDB files, writes current state through internal winreg RPC, and renames source TDBs as a completion marker. It does not wrap multi-file migration in a transaction, so partial migration is possible if a later file fails.

Dependencies and integration: depends on TDB iteration helpers, filesystem paths, `make_session_info_system()`, `rpc_pipe_open_interface()` for `ndr_table_winreg`, Samba messaging, and the per-record migration API. It is a startup/upgrade helper used before old printing databases are retired.

Risks: failures after some records have been written may leave a partly migrated registry with the original TDB still present. Rename failure is logged but does not change the success return from `migrate_internal()`. Iteration must free TDB keys and fetched data correctly. Tests should cover no-file success, malformed TDB records, order-dependent secdesc migration, missing printer secdesc skip, winreg pipe failures, and `.bak` rename behavior.
