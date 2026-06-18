# sources/user-network-fs/impacket/impacket/dcerpc/v5/mimilib.py

## Purpose

`mimilib.py` implements a small DCE/RPC interface for the Mimikatz RPC service based on gentilkiwi's IDL. It defines bind/unbind/command calls and helper code for Diffie-Hellman public-key exchange material used by the client-side workflow.

## Important APIs, Types, and Functions

`MSRPC_UUID_MIMIKATZ` identifies the interface. `DCERPCSessionError` formats NTSTATUS errors. Crypto blob structures built on Impacket `Structure` include `PUBLICKEYSTRUC`, `DHPUBKEY`, and `PUBLICKEYBLOB`; NDR types include `MIMI_HANDLE`, `BYTE_ARRAY`, `PBYTE_ARRAY`, `MIMI_PUBLICKEY`, and `PMIMI_PUBLICKEY`. RPC call classes are `MimiBind`, `MimiUnbind`, and `MimiCommand` with matching responses, registered in `OPNUMS` for opnums 0, 1, and 2. `MimiDiffeH` computes 1024-bit modular DH public values and shared secrets. Helpers `hMimiBind` and `hMimiCommand` populate request objects.

## Control Flow

A caller generates a public key, wraps it in `MIMI_PUBLICKEY`, calls `hMimiBind`, receives a server public key and `MIMI_HANDLE`, derives a shared secret externally, encrypts command bytes externally, and sends them with `hMimiCommand`. `hMimiCommand` sets the command length and stores the encrypted command as a conformant byte array.

## State and Persistence Behavior

The module maintains local ephemeral DH values inside each `MimiDiffeH` instance: generator, prime, private key, public key, and shared secret. Remote state is represented by the `MIMI_HANDLE` returned from bind and consumed by command/unbind. No files or durable state are written.

## Dependencies and Integration Points

It depends on `binascii`, Python `random`, Impacket dtypes/NDR/rpcrt/Structure, UUID conversion, and `nt_errors`. It integrates with DCE/RPC transports and any external command encryption/decryption logic used by Mimikatz RPC clients.

## Risks and Edge Cases

`MimiDiffeH` uses Python's `random.getrandbits`, which is not a cryptographic RNG. The module does not implement the command encryption layer, RC4 use, padding, or response decryption; callers must apply the correct protocol behavior around these raw request classes. Public key byte conversion strips leading zeroes unless hex normalization happens to preserve them, so fixed-size blob construction should be tested. This interface is explicitly security-sensitive and generally associated with credential tooling.

## Test Signals

Tests should cover DH toy-vector behavior from the `__main__` block, public-key blob layout, bind request serialization, command length/count handling, and fake-DCE helper assertions. Integration testing should use an isolated lab service only.
