# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_mit.c

## Purpose

This MIT Kerberos-specific file implements `smb_krb5_rd_req_decoded()` for the raw Kerberos GENSEC backend. It accepts an AP-REQ with MIT APIs, retrieves a long-term key from the keytab for PAC verification, and creates the AP-REP reply.

## Important APIs And Functions

`smb_krb5_get_longterm_key()` looks up a keytab entry for the ticket server principal, key version, and enctype with `krb5_kt_get_entry()`, copies the keyblock with `krb5_copy_keyblock()`, and frees the keytab entry.

`smb_krb5_rd_req_decoded()` calls `krb5_rd_req()` to accept the request, uses `smb_krb5_get_longterm_key()` to obtain the keyblock, and calls `krb5_mk_rep()` to produce the reply.

## Control Flow

Outputs are initialized to null/zero. The function accepts the AP-REQ with `krb5_rd_req()`, passing the auth context, optional acceptor principal, keytab, AP options output, and ticket output. It then retrieves the long-term key using the accepted ticket's server principal, kvno `0` for latest key, and ticket enctype. Finally it creates an AP-REP with `krb5_mk_rep()`. Failures after ticket allocation free the ticket; failures after key allocation free both ticket and keyblock.

## State And Persistence

No persistent state is stored. On success, ownership of `ticket`, `keyblock`, and `reply` transfers to the caller. The helper deliberately retrieves the long-term key from the keytab, not merely a subkey, because PAC signature verification needs it.

## Dependencies And Integration Points

It depends on MIT Kerberos APIs, Samba Kerberos includes, and the common `gensec_krb5.h` declaration. `gensec_krb5.c` uses this function in server-side raw Kerberos authentication on MIT builds.

## Risks And Edge Cases

The comment notes a FIXME around using `ticket->enc_part.kvno`; the code passes `0` to get the latest kvno because this fixes a winbind PAC AD member test. That is a compatibility tradeoff and could matter in key rollover scenarios. Keytab lookup failures prevent PAC verification and abort authentication. Memory cleanup on each failure path is security and stability sensitive.

## Test Signals

MIT builds should test AP-REQ accept, AP-REP generation, PAC verification with the returned long-term key, key rollover/latest kvno behavior, missing keytab entries, wrong enctype/principal, and leak-free failure after ticket or keyblock allocation.
