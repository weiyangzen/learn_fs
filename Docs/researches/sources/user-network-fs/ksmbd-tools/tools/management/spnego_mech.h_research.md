# sources/user-network-fs/ksmbd-tools/tools/management/spnego_mech.h

## Purpose

`spnego_mech.h` defines the private mechanism interface shared by SPNEGO negotiation and Kerberos mechanism implementations. It declares mechanism identifiers, the response encoder callback type, operation vtable, mechanism context layout, and exported krb5 operation tables. The source was read as a complete 48-line file.

## Important APIs, Types, and Functions

Important declarations are `SPNEGO_MECH_MSKRB5`, `SPNEGO_MECH_KRB5`, `SPNEGO_MAX_MECHS`, `spnego_encode_t`, `struct spnego_mech_operations`, `struct spnego_mech_ctx`, `spnego_krb5_operations`, and `spnego_mskrb5_operations`.

## Control Flow

There is no executable flow. `spnego.c` fills `spnego_mech_ctx` entries with operation pointers and parameters, calls `setup`, and later calls `handle_authen`. Mechanism implementations call the `spnego_encode_t` callback to package their output token.

## State and Persistence Behavior

The header defines context fields for OID metadata, private mechanism state, and Kerberos keytab/service parameters. Actual storage is the static context array in `spnego.c`.

## Dependencies and Integration Points

It is included by `spnego.c` and `spnego_krb5.c` and depends on `ksmbd_spnego_auth_out` being visible through surrounding includes.

## Risks and Edge Cases

The Kerberos parameter fields are typed as `void *` despite holding string pointers, weakening compile-time checks. Adding mechanisms requires increasing the enum and ensuring every slot has valid operations before `spnego_init` iterates it.

## Test Signals

Build coverage with and without Kerberos, plus compiler warnings under stricter pointer diagnostics, are the key signals.
