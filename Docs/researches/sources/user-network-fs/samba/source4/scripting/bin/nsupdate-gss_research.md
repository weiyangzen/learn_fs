<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/nsupdate-gss -->
# sources/user-network-fs/samba/source4/scripting/bin/nsupdate-gss

## Purpose

`nsupdate-gss` performs GSS-TSIG authenticated dynamic DNS updates against a Windows-compatible DNS server.

## Important APIs, Types, and Functions

Options include `--wipe`, `--add`, `--realm`, `--nameserver`, `--ntype`, `--noverify`, and `--verbose`. Key functions are `gss_sign()`, `sig_verify()`, `find_nameserver()`, `find_server_name()`, and `negotiate_tkey()`.

## Control Flow

The script accepts `HOST DOMAIN TARGET TTL`. It finds or uses a nameserver, creates a DNS resolver, generates a random TKEY name, acquires initiating GSS credentials for `dns/server@REALM`, performs a two-step TKEY negotiation, optionally verifies the MIC on the reply, builds a dynamic update that deletes old records unless `--add`, adds a new record unless `--wipe`, signs with TSIG using the GSS context, sends the update, and exits nonzero on failed rcode.

## State and Persistence Behavior

It mutates DNS records on the target server. It stores no local persistent state.

## Dependencies and Integration Points

It depends on Perl `Net::DNS`, `GSSAPI`, Kerberos credentials, DNS TKEY/TSIG support, and AD DNS naming conventions.

## Risks and Edge Cases

The script assumes one GSS continuation step is enough. It uses a random numeric key name without collision checking. `--noverify` weakens reply integrity checks. DNS update semantics differ for `--wipe`, `--add`, record type, and TTL.

## Test Signals

Tests should cover TKEY negotiation, MIC verification failure, add versus replace versus wipe, explicit nameserver, non-A record types, missing Kerberos creds, NXDOMAIN/YXDOMAIN behavior, and DNS rcode handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/nsupdate-gss -->
