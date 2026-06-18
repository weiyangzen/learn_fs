
## sources/storage-engines/wiredtiger/ext/encryptors/nop/nop_encrypt.c

Purpose: sample `WT_ENCRYPTOR` implementation that copies bytes unchanged while demonstrating encryptor customization.

Important APIs/functions: `NOP_ENCRYPTOR` embeds `WT_ENCRYPTOR`, stores extension API, and counts calls. `nop_encrypt` checks destination capacity and copies source. `nop_decrypt` copies `dst_len` bytes and reports that length. `nop_sizing` reports zero expansion. `nop_customize` copies the encryptor, reads `keyid` and `secretkey`, rejects specifying both, allows neither for tests, and does not install real key material. `wiredtiger_extension_init` registers `nop`.

State and persistence: customized encryptor instances are heap objects; no persistent format overhead because ciphertext equals plaintext. Risks: this is not encryption; decrypt trusts caller-provided output length; keys are parsed only as demonstration. Tests should cover customize with keyid, secretkey, both, neither, capacity errors, pass-through round trips, and terminate of customized and original instances.
