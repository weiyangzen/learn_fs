# sources/user-network-fs/samba/source3/libads/sasl.c

## Purpose

`sasl.c` performs ADS LDAP SASL/SPNEGO binds using Samba GENSEC credentials, chooses LDAP signing/sealing behavior, applies TLS channel bindings, and provides a helper for building simple `cli_credentials`.

## Important APIs, Types, and Functions

`ads_simple_creds` constructs credentials from domain, account name, and password. `ads_sasl_bind` is the public bind entry point. Internal functions include `ads_sasl_spnego_bind`, `ads_sasl_spnego_gensec_bind`, `ads_guess_target`, `ads_generate_service_principal`, and GENSEC wrap hooks `ads_sasl_gensec_wrap`, `ads_sasl_gensec_unwrap`, and `ads_sasl_gensec_disconnect`. `struct ads_service_principal` tracks generated LDAP service, host, and principal strings.

## Control Flow

`ads_sasl_bind` maps auth flags to wrap type: LDAPS/StartTLS use plain SASL over TLS, seal requests signing and sealing, sign requests signing, and the default is plain. TLS modes require channel bindings from `ads_tls_channel_bindings`. The SPNEGO path guesses `ldap/<server>@<realm>`, configures target service/hostname, sets GENSEC channel bindings when available, requests GENSEC features for sign/seal modes, starts the client by SASL name `GSS-SPNEGO`, then loops `gensec_update` tokens through `ldap_sasl_bind_s` until both LDAP and GENSEC complete.

After bind, it verifies requested sign/seal features, records credential expiry, computes wrapping sizes, and installs the SASL sockbuf wrapper when wrap type is sign or seal. If a plain non-TLS bind receives `LDAP_STRONG_AUTH_REQUIRED`, it retries with signing enabled.

## State and Persistence Behavior

State mutates `ads->ldap_wrap_data` wrap type, ops, private GENSEC pointer, buffer sizing, and `ads->auth.expire_time`. GENSEC state is retained past bind only when socket wrapping is installed. `ads_simple_creds` returns caller-owned `cli_credentials`.

## Dependencies and Integration Points

Dependencies include `cli_credentials`, loadparm context initialization, GENSEC/auth_generic, OpenLDAP SASL bind APIs, Kerberos support for target principal generation, TLS channel binding data from `tls_wrapping.c`, and SASL wrapping from `sasl_wrapping.c`. It integrates with `ads_connect_internal`.

## Risks and Test Signals

Risks include target-name guesses for short/non-FQDN server names, channel-binding absence under TLS, feature negotiation mismatches, token-loop termination errors, fallback from plain to sign changing security expectations, and retained GENSEC lifetime management. Tests should cover simple creds, Kerberos and NTLMSSP SPNEGO, LDAPS/StartTLS with channel bindings, sign/seal feature verification, strong-auth retry, generated service principal cases, expiry propagation, and installed wrapper encrypt/decrypt round trips.
