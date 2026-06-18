# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_heimdal.c

## Purpose

This Heimdal-specific file implements `smb_krb5_rd_req_decoded()` for the raw Kerberos GENSEC backend using Heimdal APIs. It preserves Heimdal license attribution because the code is derived from Heimdal acceptor logic.

## Important API And Functions

The sole function is `smb_krb5_rd_req_decoded()`. It uses Heimdal `krb5_rd_req_in_ctx` and `krb5_rd_req_out_ctx` objects, `krb5_rd_req_in_set_keytab()`, `krb5_rd_req_ctx()`, `krb5_rd_req_out_get_ticket()`, `krb5_rd_req_out_get_keyblock()`, and `krb5_mk_rep()`.

## Control Flow

The function initializes output pointers and AP-REP buffer to null/zero, allocates an input context, attaches the keytab, and calls `krb5_rd_req_ctx()` with the input token and optional acceptor principal. After successful acceptance it extracts the decoded ticket and keyblock from the output context, frees the output context, then creates an AP-REP with `krb5_mk_rep()`. On any error after outputs are allocated, it frees ticket, keyblock, and output data before returning the Kerberos error.

## State And Persistence

No long-lived state is created. The decoded ticket, keyblock, and AP-REP data are returned to the caller for storage in `gensec_krb5_state`. Temporary Heimdal contexts are freed before return.

## Dependencies And Integration Points

It depends on Heimdal Kerberos APIs, Samba Kerberos includes, and the common declaration in `gensec_krb5.h`. It is selected in Heimdal builds and called from `gensec_krb5.c` server-side AP-REQ processing.

## Risks And Edge Cases

Memory ownership is the main risk: partial ticket/keyblock/outbuf outputs must be freed on failure. The input context must always be freed after use. The helper assumes Heimdal can return the keyblock directly from `krb5_rd_req_out_get_keyblock()`, unlike the MIT implementation that looks up a long-term key separately.

## Test Signals

Heimdal builds should test successful AP-REQ accept, generated AP-REP, PAC verification using the returned keyblock, bad keytab or principal errors, and leak checks around failure paths after ticket or keyblock extraction.
