# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_base.sh

Purpose: runs a small set of Samba `BASE-*` smbtorture tests against a Windows server share created by expect setup scripts.

Control flow: it sources selftest and Windows helpers, validates `SERVER USERNAME PASSWORD DOMAIN`, exports `SMBTORTURE_REMOTE_HOST`, then loops over `BASE-UNLINK`, `BASE-ATTR`, `BASE-DELETE`, `BASE-TCON`, `BASE-OPEN`, and `BASE-CHKPATH`. Each test performs `setup_share_test`, invokes `$SMBTORTURE_BIN_PATH` against `//$server/$SMBTORTURE_REMOTE_SHARE_NAME`, then runs `remove_share_test` or restores the snapshot on setup/test/cleanup failure.

State and dependencies: expect scripts create and remove Windows shares/directories; VMware snapshot restore is the recovery path. Dependencies include `WINTESTCONF`, expect, smbtorture, Windows credentials, and a configured VM.

Risks and test signals: the local `err` variable is not reset inside the loop after a failure, so later tests may be treated as failed even if smbtorture succeeds. Exit code is accumulated `all_errs`.
