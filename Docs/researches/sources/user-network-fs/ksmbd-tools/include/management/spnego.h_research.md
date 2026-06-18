<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/spnego.h -->
# sources/user-network-fs/ksmbd-tools/include/management/spnego.h

## Purpose

Declares SPNEGO authentication handling for mountd.

## Important APIs, Types, and Functions

Exposes `spnego_handle_authen_request(struct ksmbd_spnego_authen_request *, struct ksmbd_spnego_authen_response *)`.

## Control Flow

The implementation consumes a kernel SPNEGO auth request, negotiates NTLM/Kerberos mechanisms as configured, and fills a combined login/SPNEGO response.

## State and Persistence Behavior

State is request/response payload memory plus any implementation-side Kerberos context; no persistence is declared here.

## Dependencies and Integration Points

Depends on `linux/ksmbd_server.h`, ASN.1 helpers, user management, and optional Kerberos config macros.

## Risks and Edge Cases

Authentication blob parsing is security-sensitive and must reject malformed ASN.1/mechanism tokens. Optional Kerberos support changes behavior at compile time.

## Test Signals

Tests need NTLM/SPNEGO negotiation vectors, Kerberos-enabled and disabled builds, malformed blobs, and response size bounds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/spnego.h -->
