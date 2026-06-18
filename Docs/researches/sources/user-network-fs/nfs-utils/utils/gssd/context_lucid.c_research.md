<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_lucid.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/context_lucid.c

## Purpose
This is the common Kerberos serializer for GSS libraries that support exported lucid security contexts. It avoids private MIT/Heimdal context layouts and chooses the kernel's legacy or v2 context format based on protocol and enctype.

## APIs And Control Flow
`serialize_krb5_ctx` calls `gss_export_lucid_sec_context` for version 1 lucid data, then dispatches to `prepare_krb5_rfc1964_buffer` when protocol is RFC1964 with DES-like enctypes, or `prepare_krb5_rfc4121_buffer` otherwise. The RFC1964 path emits legacy fields, Kerberos OID, an XOR-derived encryption key, and sequence key. The RFC4121 path emits v2 flags, endtime, 64-bit send sequence, selected enctype, and raw key bytes, preferring acceptor subkey when present. It frees lucid context data through `gss_free_lucid_sec_context`.

## State, Dependencies, And Integration
No persistent state is stored. Dependencies are `gssapi_krb5.h`, gss_util compatibility macros, `krb5oid`, `write_bytes.h`, and `context.h`. This backend is the preferred serializer when configure detects lucid support.

## Risks And Test Signals
Risks include version-1-only lucid support, context export consuming or invalidating the original context, duplicated flag constants, DES key derivation compatibility, and key choice differences for acceptor subkeys. Test with MIT and Heimdal lucid builds, DES/DES3/RC4/AES enctypes, CFX and non-CFX protocols, acceptor subkey cases, and failure to free lucid contexts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_lucid.c -->
