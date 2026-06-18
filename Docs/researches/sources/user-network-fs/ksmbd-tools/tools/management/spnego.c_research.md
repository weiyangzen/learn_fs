# sources/user-network-fs/ksmbd-tools/tools/management/spnego.c

## Purpose

`spnego.c` implements SPNEGO token negotiation glue for ksmbd Kerberos authentication. It initializes supported mechanisms, decodes incoming `negTokenInit` ASN.1 blobs, extracts the Kerberos AP_REQ, selects MS-KRB5 or standard KRB5 by OID, and wraps mechanism AP_REP output into a `negTokenTarg` response. The source was read as a complete 339-line file.

## Important APIs, Types, and Functions

Public functions are `spnego_init`, `spnego_destroy`, and `spnego_handle_authen_request`. Important internals are `get_mech`, `compare_oid`, `is_supported_mech`, `decode_asn1_header`, `decode_negTokenInit`, and `encode_negTokenTarg`. State is the static `mech_ctxs[SPNEGO_MAX_MECHS]` array of `spnego_mech_ctx`.

## Control Flow

Initialization assigns operations and global Kerberos service/keytab parameters to MSKRB5 and KRB5 contexts, then calls each mechanism setup. Authentication decodes the outer GSS/SPNEGO layers, validates SPNEGO and Kerberos OIDs, extracts the AP_REQ bytes, finds the selected mechanism context, and invokes its `handle_authen` callback with `encode_negTokenTarg` as a response encoder.

## State and Persistence Behavior

Mechanism contexts persist for the mountd process lifetime and are cleaned up by `spnego_destroy`. Per-request output buffers are allocated by the mechanism/encoder and freed by the worker after IPC response construction.

## Dependencies and Integration Points

It depends on `asn1.c`, `spnego_mech.h`, `management/spnego.h`, global config, and `spnego_krb5.c` operations. It is called from `mountd/worker.c` for `KSMBD_EVENT_SPNEGO_AUTHEN_REQUEST`.

## Risks and Edge Cases

The decoder accepts only the expected token shape and first mechanism OID; clients offering multiple mechanisms or unusual optional SPNEGO fields may fail. `spnego_init` assumes non-null operations before testing `mech_ctxs[i].ops->setup`, so all mechanism slots must be initialized. ASN.1 length and pointer handling is security-sensitive because blobs originate from clients.

## Test Signals

Valid Windows Kerberos negotiation, unsupported OID rejection, malformed/truncated SPNEGO fuzz cases, krb5-disabled builds, and cleanup/reinit tests are the core signals.
