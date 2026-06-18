# File Research: sources/os/bsd/netbsd-src/lib/libwrap/eval.c

## Purpose
Lazy evaluation and caching of request user, host address, host name, client, and server strings.

## Key Details
- Exposes global `unknown` and `paranoid` strings.
- `eval_user` performs RFC931 lookup only when needed and possible.
- `eval_hostaddr` and `eval_hostname` call request-provided resolver hooks.
- `eval_hostinfo` prefers hostname when known, otherwise address.
- `eval_client` and `eval_server` compose user/host and daemon/host strings.

## Dependencies and Role
- Avoids unnecessary network lookups during access checks.
