# sources/user-network-fs/samba/source3/libads/tls_wrapping.c

## Purpose

`tls_wrapping.c` installs a synchronous TLS layer into OpenLDAP's sockbuf stack for ADS LDAPS and StartTLS connections, and exposes channel bindings for SASL.

## Important APIs, Types, and Functions

`ndr_print_ads_tlswrap_struct` prints TLS wrapper state. `ads_setup_tls_wrapping` is the main setup API. `ads_tls_channel_bindings` returns TLS channel binding data. Internal OpenLDAP sockbuf callbacks include setup/remove, read/write, ctrl, close, and GnuTLS transport send/recv shims.

## Control Flow

Setup obtains the LDAP sockbuf, initializes a Samba loadparm context, builds client TLS parameters for the server name, adds the TLS sockbuf layer, sets an endtime from LDAP connection timeout, performs synchronous TLS setup using callbacks that read/write the underlying sockbuf, clears the endtime, and removes the IO layer if the handshake fails. After setup, LDAP reads/writes pass through `tstream_tls_sync_read/write`, while `DATA_READY` checks pending decrypted TLS bytes before delegating.

## State and Persistence Behavior

State is held in `struct ads_tlswrap`: memory context, sockbuf descriptor, TLS params, sync TLS context, and temporary handshake deadline. It lasts for the LDAP connection and is freed on sockbuf close or `ads_disconnect`. Channel binding data is derived from the live TLS context.

## Dependencies and Integration Points

It depends on OpenLDAP sockbuf APIs, Samba source4 TLS helpers, GnuTLS transport callbacks, loadparm TLS configuration, and ADS connection code. `sasl.c` uses `ads_tls_channel_bindings` to bind SASL authentication to the TLS channel.

## Risks and Test Signals

Risks include handshake timeout mapping to `ECONNRESET`, TLS parameter/config errors, IO layer cleanup on partial failure, channel bindings unavailable before setup, and sync TLS calls inside OpenLDAP's blocking expectations. Tests should cover LDAPS and StartTLS handshakes, certificate policy failures, timeout behavior, pending-data `DATA_READY`, channel binding availability, and cleanup after handshake failure.
