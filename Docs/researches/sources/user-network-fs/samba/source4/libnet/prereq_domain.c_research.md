# sources/user-network-fs/samba/source4/libnet/prereq_domain.c

## Purpose

`prereq_domain.c` provides prerequisite helpers that ensure a SAMR or LSA domain handle is open before higher-level libnet composite operations continue. It centralizes cached-handle reuse and async `libnet_DomainOpen` scheduling.

## Important APIs, Types, and Functions

`samr_domain_opened()` checks `ctx->samr.handle` and `ctx->samr.name`; if the requested domain is not already open, it fills `libnet_DomainOpen` for `DOMAIN_SAMR` and starts `libnet_DomainOpen_send()`.

`lsa_domain_opened()` mirrors the logic for `ctx->lsa.handle`, `ctx->lsa.name`, and `DOMAIN_LSA`.

Both accept a parent composite context pointer, a continuation callback, and a monitor callback. They return `true` when the prerequisite is already satisfied or a terminal error has been placed on the parent, and `false` when an async open request has been queued.

## Control Flow

If `domain_name` is NULL and no handle is cached, the helpers use `cli_credentials_get_domain(ctx->cred)`. If `domain_name` is non-NULL and the cached handle is empty or for a different domain, they schedule domain open. If the matching handle already exists, they return true so callers can continue immediately. If NULL domain is supplied while a handle already exists, they signal invalid parameter.

## State and Persistence Behavior

The functions mutate no persistent directory state directly. They may initiate `libnet_DomainOpen`, whose receive path updates `libnet_context` cached SAMR/LSA handles and names. The helpers affect control state in parent composite contexts.

## Dependencies and Integration Points

Dependencies include composite async helpers, credentials, NDR policy-handle emptiness checks, generated SAMR/LSA headers, and `libnet_DomainOpen`. `libnet_user.c` and other libnet domain operations depend on this for precondition handling.

## Risks and Edge Cases

The boolean return convention is subtle: true can mean "ready" or "error already set"; false can mean "async request queued". Callers must follow the pattern exactly. `lsa_domain_opened()` returns true on `composite_nomem()` while SAMR returns false, which is an inconsistency. NULL-domain behavior rejects calls when a handle is already open instead of assuming reuse, which may surprise callers.

## Test Signals

Tests should cover already-open same domain, open different domain, NULL domain with and without cached handles, allocation failure simulation, continuation invocation, and both SAMR and LSA branches.
