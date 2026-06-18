<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/context.c

## Purpose
This file is the mechanism dispatcher for serializing established GSS contexts into the kernel format expected by RPCSEC_GSS. It currently accepts only Kerberos V5.

## APIs And Control Flow
`serialize_context_for_kernel` receives a `gss_ctx_id_t`, output buffer, mechanism OID, and optional endtime pointer. It compares the supplied OID with the global Kerberos OID through `g_OID_equal`; Kerberos is delegated to `serialize_krb5_ctx`, while any other mechanism logs an unsupported-mechanism error and returns `-1`.

## State, Dependencies, And Integration
There is no private state. Dependencies are GSSAPI types, `krb5oid` from `gss_oids.c`, the selected `serialize_krb5_ctx` implementation from the conditional context backend, and `printerr` logging. It is called by `gssd_proc.c` after creating an authenticated RPCSEC_GSS context and before writing a downcall to the kernel pipe.

## Risks And Test Signals
Risks are intentionally narrow mechanism support and OID comparison assumptions. Tests should cover successful Kerberos dispatch, unsupported OID failure, null/invalid OID defensive behavior at callers, and builds selecting lucid, MIT-private, or Heimdal serializers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context.c -->
