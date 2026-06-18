# sources/user-network-fs/samba/source3/libads/ldap_user.c

## Purpose

`ldap_user.c` contains simple ADS LDAP helpers for finding and creating AD user and group accounts.

## Important APIs, Types, and Functions

`ads_find_user_acct` searches by escaped `sAMAccountName`. `ads_add_user_acct` creates a disabled normal user with `top/person/organizationalPerson/user` object classes, UPN, display name, and `sAMAccountName`. `ads_add_group_acct` creates a `top/group` object with optional description.

## Control Flow

The find path escapes the LDAP filter value, builds `(sAMAccountName=value)`, and delegates to `ads_search`. User creation picks `fullname` or `user` as CN/display name, escapes the RDN, builds `cn=<name>,<container>,<bind_path>`, sets `UF_NORMAL_ACCOUNT|UF_ACCOUNTDISABLE`, builds a mod list, and calls `ads_gen_add`. Group creation follows the same DN and mod-list pattern with group object classes and optional description.

## State and Persistence Behavior

The file owns no local state. Successful add operations persist new AD objects. Temporary DNs, escaped names, UPN strings, and mod lists are talloc/heap owned and freed before return.

## Dependencies and Integration Points

It depends on ADS search/add/mod helpers, AD account-control flags, LDAP and RDN escaping utilities, and `ads->config.realm`/`bind_path`. It integrates with administrative account creation paths in Samba tools.

## Risks and Test Signals

Risks include insufficient escaping if `container` is caller-provided malformed DN text, creating disabled users without password setup, duplicate `sAMAccountName`, and unclear behavior when ADS config lacks realm or bind path. Tests should cover special-character usernames/full names, duplicate and missing container failures, optional group comments, disabled-account flags, and LDAP filter escaping.
