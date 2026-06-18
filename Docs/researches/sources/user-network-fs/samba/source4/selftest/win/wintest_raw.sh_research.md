# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_raw.sh

Purpose: runs raw SMB file operation smbtorture tests against a Windows server share.

Control flow: it validates server credentials, exports `SMBTORTURE_REMOTE_HOST`, loops over RAW tests such as qfileinfo, sfileinfo, mkdir, seek, open, write, unlink, read, close, ioctl, rename, EAs, and streams. For each test it creates the Windows share via expect, runs smbtorture against `//$server/$SMBTORTURE_REMOTE_SHARE_NAME`, then cleans up or restores snapshot.

State and dependencies: setup and cleanup mutate the Windows VM filesystem/share configuration. Dependencies mirror `wintest_base.sh`.

Risks and test signals: `err` is not reset per test after failure. `RAW-QFSINFO` is deliberately excluded as failing. Exit status is the accumulated error count after any snapshot recovery.
