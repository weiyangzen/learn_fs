# sources/user-network-fs/samba/source3/script/tests/test_usershare_not_accessible.sh

Purpose: regression test for a usershare lifetime crash where removing a usershare definition during an active connection could destroy service state still referenced by an existing tree connect, later causing a null dereference during `volume` handling.

Important functions and APIs: uses `net usershare`, `testparm --parameter-name="usershare path"`, interactive `smbclient`, named FIFOs, and subunit primitives. `cleanup()` removes the test usershare file, directory, and FIFO artifacts.

Control flow: the script discovers the usershare path, creates a backing directory and usershare, starts a persistent forced-interactive `smbclient` connected to that usershare, verifies `ls`, records the current client tree id, deletes the usershare definition file, issues a new `tcon` to force `find_service()`/`usershare_exists()` failure, restores the original tid, runs `volume`, then runs `ls` and checks whether the server stayed alive.

State and persistence: creates a usershare definition, a backing directory under `$LOCAL_PATH/usershares`, and named pipes in `$SELFTEST_TMPDIR`. It removes these at startup and exit, although abnormal exits can leave the usershare directory or definition until the next cleanup.

Dependencies and integration: registered as `samba3.blackbox.usershare_not_accessible` in `fileserver:local`. It relies on smbclient interactive commands (`tid`, `tcon`, `volume`), usershare support, and a server build with the crash path fixed.

Risks and test signals: FIFO timing uses sleeps and fixed reads, so slow environments can make output parsing fragile. Passing signal is a final directory listing containing `.` and no `NT_STATUS_CONNECTION_DISCONNECTED`; failure output captures the smbclient transcript.
