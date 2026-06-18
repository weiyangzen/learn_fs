# sources/user-network-fs/samba/source3/libads/net_ads_setspn.c

## Purpose

`net_ads_setspn.c` implements `net ads setspn` operations for listing, adding, and deleting service principal names on a machine account.

## Important APIs, Types, and Functions

Public functions are `ads_setspn_list`, `ads_setspn_add`, and `ads_setspn_delete`. Internal `find_spn_in_spnlist` performs case-insensitive duplicate detection. The file uses `parse_spn`, `ads_get_service_principal_names`, `ads_add_service_principal_names`, `ads_find_machine_acct`, `ads_mod_strlist`, `ads_get_dn`, and `ads_gen_mod`.

## Control Flow

List fetches SPNs and prints each value. Add parses the requested SPN for basic syntax, reads existing SPNs, rejects case-insensitive duplicates, then appends the new SPN through `ads_add_service_principal_names`. Delete lowercases the target, loads the machine object and current SPN list, builds a new NULL-terminated list excluding case-insensitive matches, then replaces the whole `servicePrincipalName` attribute on the object DN.

## State and Persistence Behavior

The only persistent state is AD's `servicePrincipalName` attribute. Temporary arrays and lowercase strings live in a stack talloc frame. Delete persists a full attribute replacement, not a single-value LDAP delete.

## Dependencies and Integration Points

It depends on ADS LDAP object helpers and `parse_spn` from `util.c`. It integrates with the `net ads setspn` command surface and with machine account/SPN management used by Kerberos service discovery.

## Risks and Test Signals

Risks include full-list replacement racing with other SPN updates, no success/failure distinction when deleting a non-existent SPN, syntax validation limited to parsing rather than checking service class semantics, and case-folding allocation failures. Tests should cover list formatting, duplicate add rejection with case variants, invalid SPN parse failures, add success, delete exact and case-variant matches, delete no-op behavior, and concurrent modification handling.
