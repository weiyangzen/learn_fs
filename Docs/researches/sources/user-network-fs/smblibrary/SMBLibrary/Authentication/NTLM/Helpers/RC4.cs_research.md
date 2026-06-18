<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/RC4.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/RC4.cs

## Purpose
`RC4` implements the RC4 stream cipher and exposes reusable key state for NTLM sealing/signing operations.

## Important APIs and Types
`Encrypt(byte[] key, byte[] data)` and `Decrypt(byte[] key, byte[] data)` initialize fresh state. `InitializeStateFromKey()` performs RC4 KSA and returns `RC4KeyState`. `Encrypt(RC4KeyState state, byte[] data)` mutates ongoing PRGA state. `RC4KeyState` stores the S-box and i/j indices.

## Control Flow
Initialization fills S with 0..255, permutes it with the key, and returns state. Encryption increments i, updates j, swaps S entries, derives the stream byte from the permuted state, and XORs input bytes. Decrypt is identical to encrypt.

## State, Dependencies, and Integration
Stateful mode is used by `NTLMCryptography.ComputeMessageSignature()` so consecutive signatures can share the sealing stream. Key-exchange decryption/encryption uses fresh state.

## Risks and Test Signals
RC4 is obsolete but required by NTLM. Empty keys would divide by zero. Stateful encryption is not thread-safe. Tests should include known RC4 vectors, fresh encrypt/decrypt symmetry, stateful multi-call equivalence to one-shot encryption, and key-exchange session-key decryption.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/RC4.cs -->
