# sources/sync-backup/borg/src/borg/platformflags.py

Purpose: centralizes platform booleans for Borg.

Important APIs/types: `is_win32`, `is_cygwin`, `is_linux`, `is_freebsd`, `is_netbsd`, `is_openbsd`, `is_darwin`, `is_haiku`, and `is_msystem`.

Control flow/state: flags are computed once at import from `sys.platform`; `is_msystem` also checks `MSYSTEM` in the environment.

Dependencies/integration: drives `platform.__init__` import selection and smaller platform-specific branches elsewhere.

Risks: monkeypatching `sys.platform` after import has no effect. Prefix checks must remain aligned with Python platform strings. MSYS2 detection is import-time environment-dependent.

Test signals: import-under-monkeypatch tests for each platform string and `MSYSTEM` handling.
