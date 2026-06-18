# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_helpers.h

## Purpose

This header declares the raw Kerberos helper that reports whether the accepted ticket is an initial Kerberos ticket.

## Important API

`int gensec_krb5_initial_ticket(const struct gensec_security *gensec_security)` returns `1` for an initial ticket, `0` for a non-initial ticket, and `-1` for errors such as wrong mechanism or missing ticket. The header forward-declares `struct gensec_security` so callers do not need the full GENSEC definition just to see the prototype.

## Control Flow

There is no executable flow. The implementation in `gensec_krb5_helpers.c` validates the mechanism, reads private Kerberos state, and checks provider-specific ticket flags.

## State And Persistence

No state is defined by the header. The function observes the existing GENSEC Kerberos state created by a completed authentication exchange.

## Dependencies And Integration Points

The header is included by callers that need ticket-type information after raw Kerberos authentication. It depends only on the `gensec_security` forward declaration and is implemented against internal Kerberos state.

## Risks And Edge Cases

Consumers must handle `-1` distinctly from a valid non-initial result. A caller that treats any non-`1` value as non-initial would conflate unavailable state with an authenticated non-initial ticket.

## Test Signals

Compile coverage for consumers and runtime coverage for all three return classes are the useful signals.
