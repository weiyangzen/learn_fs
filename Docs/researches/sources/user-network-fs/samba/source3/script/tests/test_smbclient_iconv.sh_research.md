# sources/user-network-fs/samba/source3/script/tests/test_smbclient_iconv.sh

## Purpose
This test ensures `smbclient ls` reports `NT_STATUS_INVALID_NETWORK_RESPONSE` when a directory listing contains a filename that cannot be converted under a forced CP850 Unix charset.

## Important APIs, Functions, and Control Flow
The script accepts `SERVER SERVER_IP SHARENAME USERNAME PASSWORD SMBCLIENT` plus optional extra args. `test_smbclient_iconv` writes a temporary client config under `$PREFIX/client/client_cp850_smbconf` that includes the normal client config, sets `unix charset = cp850`, and sets `client min protocol = core`. It executes `CLI_FORCE_INTERACTIVE=yes smbclient ... -c ls`, captures stderr/stdout, removes the config, and greps for the expected status.

## State, Dependencies, Integration, and Risks
State is limited to the generated config file. Integration depends on `$PREFIX/client/client.conf`, a share populated with an invalid CP850 name, and Samba charset conversion code. The `eval`-constructed command is sensitive to quoting in `ADDARGS`. The test signal is the presence of the exact `NT_STATUS_INVALID_NETWORK_RESPONSE` string.
