<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/context.h

## Purpose
This header defines the GSS context serialization interface shared by gssd, svcgssd, and Kerberos-specific backend files. It also records the kernel v2 Kerberos context flag values.

## APIs And Types
`MAX_CTX_LEN` fixes the temporary serialized buffer size at 4096 bytes. Flags are `KRB5_CTX_FLAG_INITIATOR`, `KRB5_CTX_FLAG_CFX`, and `KRB5_CTX_FLAG_ACCEPTOR_SUBKEY`. Public functions are `serialize_context_for_kernel` for mechanism dispatch and `serialize_krb5_ctx` for backend-specific Kerberos serialization.

## State, Dependencies, And Integration
The header depends on RPC/GSS types and is included by context backends and upcall handling code. Its constants must match the kernel RPCSEC_GSS context import formats for legacy RFC1964 and newer RFC4121/CFX contexts.

## Risks And Test Signals
Risks include the fixed maximum length silently constraining future algorithms or token formats, duplicate flag definitions in `context_lucid.c`, and ABI dependence on kernel expectations. Test by serializing DES, DES3, RC4, AES, initiator/acceptor, and acceptor-subkey contexts and confirming kernel import succeeds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context.h -->
