# sources/user-network-fs/samba/source3/script/tests/test_smbclient_list_servers.sh

## Purpose
This regression test covers Bug 14939: listing servers via `smbclient -L` on NetBIOS port 139 must not emit the internal `smb1cli_req_writev_submit:` error when negotiating modern dialects.

## Important APIs, Functions, and Control Flow
The script accepts server, IP, username, password, and `SMBCLIENT`. `test_smbclient_list_servers` runs `CLI_FORCE_INTERACTIVE=yes $SMBCLIENT -L //$SERVER -U... -I $SERVER_IP -p139 "$ADDARGS" </dev/null 2>&1`, captures output, and fails if the internal error marker is present.

## State, Dependencies, Integration, and Risks
It has no persistent state. Integration depends on NetBIOS port 139 availability, the server list path in `smbclient`, and test credentials. Because success is "absence of a string", unrelated command failures without that string could be underdetected unless command status also fails through shell evaluation. The test signal is negative grep plus subunit status.
