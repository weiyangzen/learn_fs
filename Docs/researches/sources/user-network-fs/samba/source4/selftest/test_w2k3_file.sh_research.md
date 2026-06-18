<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_w2k3_file.sh -->
# sources/user-network-fs/samba/source4/selftest/test_w2k3_file.sh

Purpose: runs SMB file-serving torture tests expected to pass against Windows Server 2003.

Important APIs/types/functions: `test_functions.sh`, `testit`, `smbtorture`, UNC target, username/password, `TORTURE_OPTIONS`, and a curated `tests` list.

Control flow: validates UNC, username, and password, shifts optional args, declares expected-failing tests for visibility, and loops through base/raw SMB tests invoking `smbtorture` with credentials.

State and persistence behavior: remote file-serving torture tests can create/delete files on the target share; the script itself writes no local state.

Dependencies and integration points: interoperability/selftest helper for Windows file server behavior baselines.

Risks: `start` argument is captured but unused. Requires a prepared writable UNC and credentials. Known failing tests are printed but not dynamically filtered from the active list if later added.

Test signals: `testit` subunit results per SMB torture test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_w2k3_file.sh -->
