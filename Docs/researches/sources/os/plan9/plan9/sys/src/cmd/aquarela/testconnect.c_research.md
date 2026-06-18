# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/testconnect.c

Diagnostic SMB client program.

Key points:
- Connects to a target server and optional share with `smbconnect`.
- Runs RAP `smbnetserverenum2` for server and domain enumeration.
- Runs a TRANS2 `FIND_FIRST2` request for `\LICENSE` and prints SID/search count/end-of-search on success.
- Frees RAP results and the SMB client.

Dependencies:
- Uses Aquarela client, RAP, and TRANS2 client APIs.

Notable behavior:
- Intended as an interactive/manual test utility, not production code.
