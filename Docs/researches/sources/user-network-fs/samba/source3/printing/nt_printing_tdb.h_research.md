# sources/user-network-fs/samba/source3/printing/nt_printing_tdb.h

Purpose: declares the legacy NT printing TDB schema upgrade entry point.

Important API: `bool nt_printing_tdb_upgrade(void);` upgrades old `ntdrivers.tdb`, `ntprinters.tdb`, and `ntforms.tdb` files to the expected version/layout.

Control flow and integration: initialization or upgrade code calls this before attempting deeper migration to winreg-backed storage. The implementation handles path discovery, TDB opening, version detection, and in-place upgrades.

State and persistence: no header-owned state. The declared function mutates persistent TDB files and version markers.

Dependencies: requires `bool` from Samba includes.

Risks and test signals: callers only receive a boolean, so logs are needed to diagnose exact upgrade failures. Build tests should verify the declaration matches implementation; integration tests should call it before `nt_printing_tdb_migrate()` on legacy fixtures.
