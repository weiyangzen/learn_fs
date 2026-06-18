<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.spnego.conf.in -->
# sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.spnego.conf.in

## Purpose

`cifs.spnego.conf.in` is a one-line request-key template for invoking `cifs.upcall` for CIFS SPNEGO keys.

## Important APIs, Types, and Functions

The template line is `create cifs.spnego * * @sbindir@/cifs.upcall %k`.

## Control Flow

Build substitution replaces `@sbindir@`; request-key executes `cifs.upcall` with the key serial when the CIFS kernel client requests `cifs.spnego`.

## State and Persistence Behavior

The installed snippet controls key instantiation behavior but does not persist credentials itself.

## Dependencies and Integration Points

It integrates request-key, the Linux CIFS client, Kerberos/GSSAPI authentication, and `cifs.upcall`.

## Risks and Edge Cases

Wrong paths or missing `cifs.upcall` break Kerberos CIFS mounts. Administrators may also need separate `dns_resolver` configuration not represented by this one-line snippet.

## Test Signals

Trigger a Kerberos CIFS mount under a test request-key setup and confirm `cifs.upcall` is invoked with the expected key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.spnego.conf.in -->
