# sources/user-network-fs/samba/source3/param/test_lp_load.c

Purpose: command-line smoke test that repeatedly calls `lp_load_with_registry_shares()` against a supplied or default config file.

Important APIs and flow: initializes locale and Samba command-line state, suppresses log level through `lpcfg_set_cmdline()`, parses `--count/-c`, chooses a config path, loops `count` times, prints success/error per load, then calls `gfree_loadparm()`.

State and persistence: exercises loadparm global state, registry share loading, config parsing, and cleanup. It does not create persistent output itself, though underlying loadparm may open registry/config databases.

Dependencies and integration: built as non-installed `test_lp_load` binary with `talloc`, `smbconf`, and `CMDLINE_S3` dependencies. Useful for manual or automated regression checks around reload idempotence and cleanup.

Risks: `atoi()` accepts invalid or negative counts silently. The test only checks boolean load success, not service contents, leaks, or exact registry behavior. Some error exits bypass `poptFreeContext()` but process termination makes that low impact.

Test signals: run with real smb.conf, registry-backed config, high `--count`, missing config, and memory checking to catch reload leaks or stale globals.
