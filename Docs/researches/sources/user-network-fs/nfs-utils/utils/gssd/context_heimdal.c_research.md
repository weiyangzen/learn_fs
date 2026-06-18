<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_heimdal.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/context_heimdal.c

## Purpose
This is the non-lucid Heimdal-specific Kerberos context serializer. It reaches into Heimdal GSS context internals and emits the legacy kernel `krb5_ctx` wire format for DES-era contexts.

## APIs And Control Flow
The file is compiled only when lucid support is absent and Heimdal is present. `write_heimdal_keyblock` writes an enctype and opaque key buffer. `write_heimdal_enc_key` obtains the local subkey, forces keytype `4` for kernel DES compatibility, derives the encryption key by XORing bytes with `0xf0`, and writes it. `write_heimdal_seq_key` obtains and writes the sequence key. `serialize_krb5_ctx` writes initiator state, fake seed fields, fixed sign/seal algorithms, lifetime/endtime, local sequence number, Kerberos OID, encryption key, and sequence key into a `MAX_CTX_LEN` buffer.

## State, Dependencies, And Integration
There is no persistent module state. It depends on Heimdal private GSS structs, krb5 auth-context accessors, `write_bytes.h`, `krb5oid`, and gssd error helpers. It integrates with `context.c` as the selected `serialize_krb5_ctx`.

## Risks And Test Signals
Risks include private Heimdal structure coupling, DES-only assumptions, hard-coded algorithm values, mutating/forcing key types, and fixed buffer size. Test with Heimdal builds lacking lucid support, DES contexts, non-DES warning paths, expired contexts, and kernel downcall acceptance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_heimdal.c -->
