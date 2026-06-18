# File Research: sources/virtualization/nbdkit/filters/luks/luks-encryption.c

Implements LUKSv1 header parsing, passphrase unlock, anti-forensic merge, and sector encryption/decryption helpers. LUKSv2 is explicitly unsupported.

The file defines packed LUKSv1 header/keyslot structures and supports AES through GnuTLS in a limited set of modes, primarily XTS and CBC. It parses `cipher_name`, `cipher_mode`, hash spec, IV generator (`plain`/`plain64`), and maps supported combinations to GnuTLS cipher IDs. ESSIV-related code is present but disabled.

`load_header()` validates disk size, magic, version, payload offset, iteration counts, master key length, keyslot flags, keyslot stripes, and key material bounds. It byte-swaps on-disk big-endian fields and logs UUID/keyslot layout.

Unlocking tries each enabled keyslot. `try_passphrase_in_keyslot()` derives a candidate key with `gnutls_pbkdf2()`, reads and decrypts AF-split key material, merges stripes with `afmerge()`, verifies the master key digest, and saves the master key on success.

`create_cipher()` initializes a GnuTLS cipher from the master key. `do_decrypt()` and `do_encrypt()` process 512-byte sectors in place, calculating IVs from sector numbers for each sector.
