# sources/user-network-fs/samba/source4/libnet/libnet_site.h

## Purpose

`libnet_site.h` declares the small request/response contract for site discovery during join.

## Important APIs, Types, and Functions

`struct libnet_JoinSite` has input `dest_address`, `netbios_name`, and `domain_dn_str`; output `error_string`, `site_name_str`, `config_dn_str`, and `server_dn_str`.

## Control Flow

The implementation fills these output strings in `libnet_FindSite()` and consumes them in `libnet_JoinSite()`.

## State and Persistence Behavior

The structure itself is transient. Output strings become persistent only when higher-level join state steals them; `libnet_JoinSite()` uses `server_dn_str` to write AD configuration state.

## Dependencies and Integration Points

It is included through libnet join-related code and ties CLDAP site discovery to LDB join updates.

## Risks and Edge Cases

The header does not document ownership or whether CLDAP failures are fatal. Callers need to inspect status and not just output pointers.

## Test Signals

Tests around `libnet_FindSite()` should assert all three output strings are populated for both CLDAP-discovered and default-site paths.
