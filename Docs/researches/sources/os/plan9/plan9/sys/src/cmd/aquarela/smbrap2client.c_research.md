# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrap2client.c

Client-side RAP transaction helpers.

Key functions:
- `smbclientrap` fills an SMB transaction for `/PIPE/LANMAN` and executes it over the client transaction method.
- `smbnetserverenum2` builds a RAP `NetServerEnum2` request, sends it, parses return parameters, copies fixed server records and referenced remarks, and returns an array of `SmbRapServerInfo1`.

Interactions:
- Uses `smbtransactionexecute`, `smbtransactionclientsend`, and `smbtransactionclientreceive`.

Notable details:
- Applies RAP converter offset before copying remark strings from output data.
