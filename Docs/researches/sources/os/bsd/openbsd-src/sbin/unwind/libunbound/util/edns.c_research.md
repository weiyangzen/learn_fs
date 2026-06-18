# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/edns.c

## Role

`edns.c` implements base EDNS utility support outside the packet parser/encoder: configured EDNS client-string lookup data and RFC9018 DNS COOKIE creation, validation, and secret rotation.

## EDNS Client Strings

`edns_strings_create()` and `edns_strings_delete()` allocate and free an `edns_strings` container with a regional allocator. `edns_strings_apply_cfg()` rebuilds the address-prefix tree from configuration entries, parsing netblocks and inserting configured strings with `edns_strings_client_insert()`.

`edns_string_addr_lookup()` looks up the best address-tree match for a client address. `edns_strings_get_mem()` reports memory use. `edns_strings_swap_tree()` swaps a live structure with prepared data, allowing config reload-style replacement.

## DNS COOKIE Handling

`edns_cookie_server_hash()` computes the RFC9018 server-cookie SipHash over client cookie, version/reserved/timestamp, and client IP. `edns_cookie_server_write()` writes version 1 cookie metadata, timestamp, and the 8-byte server hash into a 24-byte cookie output.

`edns_cookie_server_validate()` accepts only 24-byte version-1 server cookies with a 16-byte secret, checks timestamp freshness using RFC1982 serial arithmetic, rejects expired/future/invalid hashes, and returns renewal status for valid cookies older than 30 minutes.

## Cookie Secret Management

`cookie_secrets_create()` allocates a locked secret history structure and marks protected fields. `cookie_secrets_delete()` destroys the lock, zeroes secrets with `explicit_bzero()`, and frees memory.

`cookie_secret_file_read()` reads up to `UNBOUND_COOKIE_HISTORY_SIZE` hex-encoded 16-byte secrets from a configured file, treats one file-open error case as non-fatal, and rejects malformed lines. `cookie_secrets_apply_cfg()` wraps this for config application.

`cookie_secrets_server_validate()` validates a cookie against active and staging secrets under lock, returning renewal for staging-secret matches. `add_cookie_secret()`, `activate_cookie_secret()`, and `drop_cookie_secret()` manage active/staging secret lifecycle and zero temporary or removed secret material.

## Research Notes

This file contains security-sensitive time and secret handling. Important invariants are the 16-byte secret size, 24-byte interoperable cookie format, IPv4 versus IPv6 hash input length, lock coverage around shared secrets, and zeroing secrets after use or removal.
