# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/enc_des.c

## Purpose
Implements Telnet ENCRYPT DES_CFB64 and DES_OFB64 methods.

## Main Interfaces
Exports `cfb64_*` and `ofb64_*` init/start/is/reply/session/keyid/printsub/encrypt/decrypt functions plus shared `fb64_*` helpers.

## Control Flow And State
Two global `struct fb` instances hold DES session key, key schedule, negotiation state, key-id state, temporary IV/feed data, and per-direction stream state.

Start negotiation for encryption sends a generated DES-encrypted IV as an `ENCRYPT_IS <type> FB64_IV` suboption once a valid session key exists. Decryption-side `fb64_is` accepts the IV, initializes the decrypt stream, and replies `FB64_IV_OK` or `FB64_IV_BAD`. Encryption-side `fb64_reply` initializes its stream after `IV_OK` and sends the default zero key id.

Session-key setup accepts only `SK_DES`, installs the DES key into both directions, initializes the DES random generator once, builds the key schedule, and restarts negotiation if start was waiting for a key.

Key-id handling accepts only a one-byte zero key id. CFB64 stores ciphertext feedback; OFB64 advances the DES output feedback stream independently of ciphertext. Decrypt functions support a special `data == -1` one-byte backup convention.

## Dependencies
Depends on telnet ENCRYPT constants, DES APIs, `encrypt_send_keyid`, `telnet_net_write`, `printsub`, and `printd`.

## Risks And Notes
DES and 64-bit feedback modes are legacy cryptography. Negotiation state is global and not per-session-safe. `ofb64_init` appears to assign `str_flagshift` through the CFB array rather than the OFB array; the field is not otherwise used in this file, but the assignment is suspicious.
