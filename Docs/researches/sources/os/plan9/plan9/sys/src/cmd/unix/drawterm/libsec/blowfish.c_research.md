# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/blowfish.c

Implements Blowfish setup and ECB/CBC encryption/decryption. It includes `os.h`, `<mp.h>`, and `<libsec.h>`, though the core is block-cipher code over `BFstate`.

The file contains the standard Blowfish initial P-box and S-box constants, static `bfencrypt`/`bfdecrypt` block transforms, and public `setupBFstate`, `bfCBCencrypt`, `bfCBCdecrypt`, `bfECBencrypt`, and `bfECBdecrypt`.

`setupBFstate` copies the key and IV, initializes state tables from the constants, XORs key material into the P-box, and repeatedly encrypts zero blocks to generate the final P-box/S-box state. ECB and CBC functions operate in place on 8-byte blocks, with CBC chaining through `s->ivec`.

The functions support partial trailing buffers by encrypting a keystream-like block and XORing the remaining bytes, preserving compatibility with the surrounding Plan 9 cryptographic conventions rather than enforcing strict block multiples.
