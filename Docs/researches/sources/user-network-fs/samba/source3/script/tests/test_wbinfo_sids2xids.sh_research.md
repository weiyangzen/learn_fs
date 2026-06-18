# sources/user-network-fs/samba/source3/script/tests/test_wbinfo_sids2xids.sh

Purpose: thin subunit wrapper around the Python integration test for `wbinfo --sids-to-unix-ids` consistency with singular SID/UID/GID conversion paths.

Important functions and APIs: constructs `WBINFO` and `NET` command variables with `VALGRIND` and `CONFIGURATION`, locates `test_wbinfo_sids2xids_int.py`, sources subunit, and runs the Python helper through one `testit` call.

Control flow: no internal assertions are implemented in the shell wrapper; all substantive control flow lives in the Python helper. The wrapper reports aggregate pass/fail with `testok`.

State and persistence: no direct state mutation except whatever the Python helper performs via `net cache del` and `wbinfo`.

Dependencies and integration: intended for source3 selftest use where `BINDIR`, `CONFIGURATION`, and Samba Python modules are available. The wrapper ensures the helper uses the same configured binaries as the rest of the selftest environment.

Risks and test signals: any quoting or whitespace in `WBINFO`/`NET` command variables is passed as positional arguments to Python and then used both as argv and shell snippets by the helper. The only shell-level signal is the helper's exit status.
