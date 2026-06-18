# sources/user-network-fs/samba/source3/printing/nt_printing_migrate_internal.h

Purpose: internal header exposing the high-level legacy NT printing TDB migration entry point.

Important API: declares `bool nt_printing_tdb_migrate(struct messaging_context *msg_ctx);`. The function uses Samba messaging while opening an internal winreg RPC pipe and migrating old print databases.

Control flow and integration: consumers call this once during initialization or upgrade handling. The implementation performs file discovery, winreg setup, per-file migration, and backup renames.

State and persistence: the declared API can mutate persistent registry-backed printer data and rename legacy TDB files to `.bak`, although the header owns no state itself.

Dependencies: requires prior declarations for `bool` and `struct messaging_context`, provided by normal Samba include ordering.

Risks and test signals: this small header is a coupling point between initialization code and the migration implementation. Build tests should ensure it remains included where the migrator is invoked; integration tests should verify the function is called with a valid messaging context and is idempotent after files are renamed.
