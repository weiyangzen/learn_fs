# sources/user-network-fs/samba/source3/script/tests/test_zero_readsize.sh

Purpose: regression test for invalid SMB2 negotiation behavior when `smb2 max read = 0` is injected into the server config.

Important functions and APIs: uses `smbcontrol smbd reload-config`, `global_inject.conf`, `dd`, forced-interactive `smbclient`, and subunit. `do_setup()` creates a test file and injects the invalid config. `do_cleanup()` removes files and the injection. `test_smb2_zero_readsize()` attempts put/get/delete through SMB2 and expects negotiation failure.

Control flow: setup writes `smb2 max read = 0`, reloads smbd, then the client script tries normal file operations against `//SERVER/SHARE`. The expected client exit status is `1` and output must contain `NT_STATUS_INVALID_NETWORK_RESPONSE`. Cleanup removes the injection and reloads smbd.

State and persistence: creates files in `$PREFIX` and writes/removes `global_inject.conf` next to the server configuration. It changes live smbd config for the duration of the test.

Dependencies and integration: registered as `samba3.blackbox.zero_readsize` in `simpleserver:local` with `-mSMB2`. It depends on `smbcontrol` reload working and the server rejecting invalid max-read negotiation consistently.

Risks and test signals: if the script exits before cleanup, the invalid config can affect later tests. The expected failure is protocol negotiation failure; a successful smbclient run is explicitly a test failure.
