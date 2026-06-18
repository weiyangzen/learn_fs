# sources/user-network-fs/samba/source3/lib/util_unixsids.c

## Purpose
This file maps Samba's Unix Users and Unix Groups SID namespaces to Unix uid/gid concepts and provides namespace detection helpers.

## Important APIs and Functions
Exports are `sid_check_is_unix_users`, `sid_check_is_in_unix_users`, `uid_to_unix_users_sid`, `gid_to_unix_groups_sid`, `unix_users_domain_name`, `sid_check_is_unix_groups`, `sid_check_is_in_unix_groups`, and `unix_groups_domain_name`.

## Control Flow and State
Namespace checks compare against `global_sid_Unix_Users` or `global_sid_Unix_Groups`; "in namespace" checks copy the SID, split off the RID, and compare the domain. UID/GID conversion composes the namespace SID with the numeric id as RID. There is no persistent state.

## Dependencies and Integration Points
It depends on SID helpers from `security.h`. It integrates with source3 identity mapping and display-name code that needs synthetic SIDs for local Unix accounts/groups.

## Risks and Test Signals
The conversion narrows `uid_t`/`gid_t` into a RID field, so platform id width and range should be tested. Null SIDs are not checked locally. Tests should cover namespace domain SIDs, domain-plus-RID SIDs, composed uid/gid SIDs, unrelated SIDs, and boundary uid/gid values.
