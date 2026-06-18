<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.upcall.rst.in -->
# sources/user-network-fs/cifs-utils/cifs.upcall.rst.in

## Purpose

`cifs.upcall.rst.in` is the manual-page template for the CIFS Kerberos/SPNEGO and DNS resolver request-key helper.

## Important APIs, Types, and Functions

The template documents CLI options `-c`, `--no-env-probe`, `--krb5conf`, `--keytab`, `--trust-dns`, `--legacy-uid`, `--expire`, and `--version`; the `GSS_USE_PROXY` environment variable; and request-key entries for `cifs.spnego` and `dns_resolver`.

## Control Flow

The build substitutes `@sbindir@` and converts the RST to `cifs.upcall.8`. The documented runtime flow is request-key invoking the helper with a key id, with different behavior for SPNEGO versus DNS resolver keys.

## State and Persistence Behavior

The document describes credential-cache probing, keytab use, default DNS resolver timeout of 600 seconds, and request-key configuration. It does not persist state itself.

## Dependencies and Integration Points

It integrates with `request-key.conf(5)`, `mount.cifs(8)`, `key.dns_resolver(8)`, Kerberos configuration, keytab files, and gssproxy.

## Risks and Edge Cases

Documentation must stay synchronized with option parsing in `cifs.upcall.c`, especially `--no-env-probe`, `--legacy-uid`, and DNS trust warnings. Incorrect request-key examples can break Kerberos mounts system-wide.

## Test Signals

Generate the manpage and compare documented options with `getopt_long` in `cifs.upcall.c`. Packaging tests should verify substituted helper paths and request-key snippets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.upcall.rst.in -->
