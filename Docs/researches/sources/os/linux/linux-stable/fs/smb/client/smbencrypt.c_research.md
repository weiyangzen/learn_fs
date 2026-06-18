# File Research: sources/os/linux/linux-stable/fs/smb/client/smbencrypt.c

## Summary
Provides the legacy SMB password-hash helper for producing an MD4 hash of a password encoded as NT Unicode. It is a small cryptographic support file used by older CIFS/NTLM authentication paths.

## Main Responsibilities
- Wrap the CIFS MD4 implementation through `mdfour()`.
- Convert an input password to UTF-16 using the supplied NLS codepage with a maximum of 128 characters.
- Hash the UTF-16 password bytes into the 16-byte NT hash buffer.
- Explicitly zero the temporary UTF-16 password buffer before returning.

## Key Interfaces
- `E_md4hash(const unsigned char *passwd, unsigned char *p16, const struct nls_table *codepage)` is the exported helper.
- Internal `mdfour()` initializes, updates, and finalizes `struct md4_ctx`.

## Important Behavior
A null password is treated as an empty UTF-16 string. The temporary password buffer is stack-allocated and then cleared with `memzero_explicit()` to avoid leaving plaintext-derived material in memory. MD4 failures are logged and returned to the caller.

## Cross-File Interactions
This helper belongs to legacy SMB/CIFS authentication support and uses `../common/md4.h` plus CIFS Unicode conversion from `cifs_unicode.h`. SMB2 raw NTLMSSP setup in `smb2pdu.c` ultimately depends on NTLM credential material prepared by surrounding CIFS authentication helpers.

## Risks
The algorithm is legacy and cryptographically obsolete, but required for NT hash compatibility. The main implementation risks are password length truncation, codepage conversion behavior, and preserving sensitive-buffer clearing on all paths.
