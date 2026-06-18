# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_client.sh

Purpose: runs an expect-driven Windows client against a Samba server share.

Control flow: it sources selftest and Windows helper scripts, sources `WINTESTCONF`, exports `SMBTORTURE_REMOTE_HOST` from the first argument, concatenates `common.exp` and `wintest_client.exp` into `$TMPDIR/client_test.exp`, runs `expect`, restores the snapshot on failure, removes the temporary expect script, and exits with `all_errs`.

State and dependencies: remote Windows drive mappings, file creation, and Samba share interaction happen inside expect scripts. It depends on `TMPDIR`, `WINTEST_DIR`, expect, and VM snapshot tooling.

Risks and test signals: `all_errs` is not initialized before arithmetic and `[ $all_errs ] >0` uses shell redirection semantics rather than a numeric comparison, which is fragile. The main signal is expect exit status.
