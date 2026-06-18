# sources/user-network-fs/samba/source3/printing/nt_printing_migrate.h

Purpose: public migration interface for translating individual legacy NT printing TDB records into the winreg-backed printing store.

Important APIs and types: declares four `NTSTATUS` functions: `printing_tdb_migrate_form()`, `printing_tdb_migrate_driver()`, `printing_tdb_migrate_printer()`, and `printing_tdb_migrate_secdesc()`. Each takes a `TALLOC_CTX`, an open `rpc_pipe_client *` for winreg, a legacy key name, raw record bytes, and record length. Driver and printer migration also accept `do_string_conversion` for ASCII legacy data.

Control flow and integration: callers choose the function based on the TDB key prefix and pass the unmodified record payload. The implementation handles NDR unmarshalling, spoolss structure mapping, and winreg calls. This header is included by both the implementation file and the internal migration walker.

State and persistence: the header itself owns no state. Its contract implies state changes through the supplied winreg pipe, so callers must already have system-level session credentials and a valid binding.

Dependencies: relies on Samba core declarations for `NTSTATUS`, `TALLOC_CTX`, `bool`, and `struct rpc_pipe_client`, normally available through `includes.h` before inclusion.

Risks and test signals: because this is a narrow ABI between TDB walking and record conversion, prototype drift would break migration at build time. Tests should compile consumers with this header and exercise all four implementation paths through the internal migrator.
