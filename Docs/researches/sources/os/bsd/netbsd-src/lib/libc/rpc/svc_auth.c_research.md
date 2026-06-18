# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_auth.c

Read completely: 220 lines.

Implements the server authentication dispatcher. `_authenticate()` copies raw credentials into the request, resets the response verifier to null auth, dispatches built-in flavors `AUTH_NULL`, `AUTH_SYS`, and `AUTH_SHORT`, and then checks a mutex-protected list of dynamically registered custom auth handlers.

`_svcauth_null()` always returns `AUTH_OK`. `svc_auth_reg()` lets services register additional credential flavors; built-in flavors return “already registered”, duplicate custom flavors are rejected, and successful registrations are permanent for the process.

This file owns auth flavor dispatch, while actual AUTH_SYS decoding is in `svc_auth_unix.c`.
