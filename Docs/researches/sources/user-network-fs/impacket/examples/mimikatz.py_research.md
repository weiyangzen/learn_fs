# sources/user-network-fs/impacket/examples/mimikatz.py

## Purpose

`mimikatz.py` is a mini shell for controlling a remote Mimikatz RPC server through Impacket's `mimilib` DCE/RPC interface. It discovers the Mimikatz endpoint, negotiates an encrypted command channel, and sends interactive or file-driven commands.

## Important APIs, Types, and Functions

`MimikatzShell` subclasses `cmd.Cmd`. Its constructor performs a Diffie-Hellman exchange with `mimilib.hMimiBind()`, derives a 16-byte RC4 key from the shared secret, and stores the remote context handle. `default(line)` UTF-16LE encodes the command, encrypts it with ARC4, calls `hMimiCommand()`, decrypts the encrypted result, and prints it. `do_shell()` runs a local OS command. `do_help()` sends the Mimikatz `::` help command. `main()` handles endpoint discovery, authentication, binding, shell creation, and command-file execution.

## Control Flow

The script first tries authenticated SMB named-pipe endpoint mapper access at `\pipe\epmapper`, with packet privacy and optional Kerberos/GSS negotiate. If Mimikatz is not registered on named pipes, or no username was supplied, it falls back to TCP endpoint mapping. After binding to `MSRPC_UUID_MIMIKATZ`, it creates `MimikatzShell`. With `-file`, non-comment lines are executed sequentially; otherwise an interactive prompt starts.

## State and Persistence Behavior

The script stores the derived RC4 key, remote Mimikatz handle, last local shell output, and DCE connection. It writes no local files by itself, but remote Mimikatz commands can have arbitrary effects depending on the server. It may reuse an SMB connection from endpoint mapping for the final bind.

## Dependencies and Integration Points

It depends on `Cryptodome.Cipher.ARC4`, Impacket EPM, `mimilib`, DCE/RPC transport, RPC privacy/auth constants, and `parse_target()`. It integrates with a separately deployed Mimikatz RPC server exposing the expected UUID.

## Risks and Edge Cases

This is highly sensitive operational tooling. If pycryptodomex is missing, the import handler logs warnings but does not exit, so later ARC4 use can fail. Endpoint discovery has multiple credential setup calls, including a second `set_credentials()` without AES key in the fallback path. Command files skip lines whose first character is `#`, but blank lines can raise indexing errors. Local `shell` commands execute on the operator machine, not the target. Debug logging may expose connection failures and details useful to attackers.

## Test Signals

Tests should mock `mimilib` bind/command calls to verify RC4 key derivation ordering, command encoding/encryption, decrypted output, file command handling, and endpoint fallback logic. Integration tests require a controlled Mimikatz RPC server and should verify SMB named-pipe binding, TCP fallback, Kerberos mode, packet privacy, and command-file behavior with comments and blank lines.
