<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_mit.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/context_mit.c

## Purpose
This is the non-lucid MIT Kerberos context serializer. It duplicates private MIT `krb5_gss_ctx_id_rec` layouts so gssd can extract keys, sequence numbers, flags, and lifetimes for kernel downcalls when lucid export APIs are unavailable.

## APIs And Control Flow
The file defines private context structs for older and newer MIT Kerberos versions plus a glue-layer `gss_union_ctx_id_t`. `write_keyblock` serializes an enctype and key contents. `serialize_krb5_ctx` unwraps the Kerberos internal context and branches on encryption type. DES-family enctypes use the legacy kernel format with initiator, seed, sign/seal algorithms, endtime, 32-bit sequence number, mech OID, encryption key, and sequence key. DES3, RC4, and AES use the v2 format with flags, endtime, 64-bit sequence, selected enctype, and either acceptor-subkey or main encryption key bytes.

## State, Dependencies, And Integration
There is no module persistence. It depends on MIT private structure compatibility, `KRB5_VERSION`, GSS glue wrapping, Kerberos enctype constants, `write_bytes.h`, and `context.h`. It is selected only without lucid support.

## Risks And Test Signals
Risks are high because private structure layouts may change, glue-layer assumptions may be wrong without libgssglue, unsupported enctypes fail, and old-format sequence truncation is intentional. Test across MIT Kerberos versions, all listed enctypes, acceptor subkey and initiator flags, unsupported enctypes, and kernel import behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_mit.c -->
