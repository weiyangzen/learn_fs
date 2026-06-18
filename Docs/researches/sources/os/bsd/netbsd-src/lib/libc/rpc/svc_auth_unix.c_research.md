# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_auth_unix.c

Read completely: 148 lines.

Implements server-side AUTH_UNIX/AUTH_SYS credential decoding. `_svcauth_unix()` decodes the credential body into the request’s cooked credential area, setting up an `authunix_parms` structure, fixed machine-name buffer, and fixed group array.

It uses an inline XDR fast path when possible, validating machine-name length against `MAX_MACHINE_NAME`, group count against `NGRPS`, and minimum encoded length against the credential length. On success it sets a null response verifier and returns `AUTH_OK`; malformed credentials return `AUTH_BADCRED`.

`_svcauth_short()` is intentionally gutted and always returns `AUTH_REJECTEDCRED`; shorthand Unix auth is not supported.
