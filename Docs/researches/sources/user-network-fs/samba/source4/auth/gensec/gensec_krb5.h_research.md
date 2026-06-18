# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5.h

## Purpose

This header declares a provider-normalized helper used by the raw Kerberos GENSEC backend to accept and decode AP-REQ tokens while also retrieving the decoded ticket and long-term key needed for PAC verification.

## Important API

`smb_krb5_rd_req_decoded()` takes a Kerberos context, auth context pointer, input AP-REQ data, keytab, optional acceptor principal, output AP-REP data, decoded ticket output, and keyblock output. It returns a Kerberos error code. The function is implemented differently for Heimdal and MIT in neighboring files but exposes a single signature to `gensec_krb5.c`.

## Control Flow

The header has no executable flow. At runtime, `gensec_krb5_update_internal()` calls this helper during server AP-REQ processing after it has acquired a keytab and chosen an acceptor principal. On success the caller stores the ticket/keyblock and sends the AP-REP output.

## State And Persistence

The helper fills caller-provided output pointers. The caller owns and later frees the decoded ticket, keyblock, and output buffer according to Kerberos provider rules. No persistent storage is defined here.

## Dependencies And Integration Points

It depends on Kerberos types from `system/kerberos.h` and Samba Kerberos helpers. It is the abstraction boundary between provider-specific Heimdal/MIT ticket decoding and the common raw GENSEC Kerberos implementation.

## Risks And Edge Cases

The contract is security-sensitive because PAC verification depends on receiving the correct long-term keyblock. Provider implementations must initialize outputs to safe defaults and free partial results on failure. A mismatch between MIT/Heimdal semantics could cause leaks, failed mutual authentication, or PAC verification with the wrong key.

## Test Signals

Server-side Kerberos GENSEC tests should confirm that both MIT and Heimdal builds produce a decoded ticket, keyblock, AP-REP, and clean failure behavior for bad tickets, missing keytab entries, and principal mismatches.
