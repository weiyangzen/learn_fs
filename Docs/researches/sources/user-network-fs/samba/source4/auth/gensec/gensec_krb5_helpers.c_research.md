# sources/user-network-fs/samba/source4/auth/gensec/gensec_krb5_helpers.c

## Purpose

This helper file exposes a small inspection API for the raw `krb5` GENSEC mechanism. It allows callers to determine whether the accepted Kerberos ticket has the initial-ticket flag set.

## Important APIs And Functions

`get_private_state()` validates that the current GENSEC mechanism name is exactly `krb5` and returns `private_data` as `struct gensec_krb5_state`. `gensec_krb5_initial_ticket()` returns `1` if the stored ticket has the initial flag, `0` if it does not, and `-1` if the mechanism is not raw krb5 or no ticket is available.

## Control Flow

`gensec_krb5_initial_ticket()` first calls `get_private_state()`. If no state or no ticket is present, it returns `-1`. Otherwise it reads the provider-specific flag location: Heimdal uses `ticket->ticket.flags.initial`; MIT uses `ticket->enc_part2->flags & TKT_FLG_INITIAL`.

## State And Persistence

The helper reads existing state only. It does not allocate, mutate, or persist data. It depends on `gensec_krb5_state->ticket` having been populated by server-side `smb_krb5_rd_req_decoded()`.

## Dependencies And Integration Points

It includes `auth/auth.h`, `auth/gensec/gensec.h`, `gensec_internal.h`, `gensec_krb5_internal.h`, Kerberos headers, and its public helper header. It integrates with code paths that need to distinguish initial tickets from non-initial service tickets after GENSEC authentication.

## Risks And Edge Cases

The mechanism-name check intentionally excludes `fake_gssapi_krb5`, even though it shares some raw Kerberos state shape. Calling before authentication completes returns `-1`. Provider-specific ticket layouts must stay aligned with MIT/Heimdal structures.

## Test Signals

Tests should call the helper after successful raw krb5 authentication with initial and non-initial tickets, before a ticket is accepted, and on non-krb5 mechanisms to verify `1`, `0`, and `-1` behavior.
