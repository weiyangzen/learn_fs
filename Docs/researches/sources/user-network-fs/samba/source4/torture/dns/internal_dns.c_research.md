# sources/user-network-fs/samba/source4/torture/dns/internal_dns.c Research

## Purpose
This file defines the `dns_internal` smbtorture suite that probes Samba's internal DNS server over DNS TCP. It verifies that the server answers an A query for its own DC hostname and refuses an unauthenticated or disallowed dynamic update for that host.

## Important APIs, Types, And Functions
`setup_connection()` opens a DNS TCP connection to `DC_SERVER_IP` with `dns_open_connection()`. `get_dns_domain()` lowercases `REALM`. `str_to_sockaddr()` converts an IPv4 string into `sockaddr_storage`. `test_internal_dns_query_self()` creates and sends an A query using `dns_create_query()` and `dns_transaction()`, then checks `dns_response_code()` for `DNS_NO_ERROR`. `test_internal_dns_update_self()` builds an update with `dns_create_update()`, creates an A record, adds it to the packet, sends it with `dns_update_transaction()`, and expects `DNS_REFUSED`.

## Control Flow
Both tests derive the FQDN as `DC_SERVER` plus lowercased `REALM`, open a connection, construct a request, execute the transaction, and validate only the DNS response code. The query test expects success. The update test attempts to add the DC server IP as a 300 second A record and expects refusal.

## State And Persistence
The query test is read-only. The update test should not persist anything because refusal is expected. Request objects are tied to the TALLOC context or DNS connection. The tests depend on environment variables and do not validate that they are present before use.

## Dependencies And Integration Points
The file uses `lib/addns/dns.h`, TALLOC, smbtorture registration, libc IPv4 parsing, and environment variables `DC_SERVER_IP`, `DC_SERVER`, and `REALM`. `torture_internal_dns_init()` registers the suite. `wscript_build` exposes it as `TORTURE_INTERNAL_DNS` in AD DC builds.

## Risks And Test Signals
The main signals are `DNS_NO_ERROR` for self query and `DNS_REFUSED` for update. The file has FIXME notes that the response body is not unmarshaled, so it cannot assert returned A data. Risks include IPv4-only update setup, missing environment validation, and false positives when a response code is correct but payload is wrong.
