# sources/user-network-fs/samba/source3/utils/net_ads_gpo.c

Purpose: implements `net ads gpo` subcommands for querying and linking Active Directory Group Policy Objects under `HAVE_ADS`.

Important APIs/types/functions: `net_ads_gpo()` dispatches `getgpo`, `linkadd`, `linkget`, `list`, and `listall`. `net_ads_gpo_list_all()` searches `groupPolicyContainer` objects including DACL data. `net_ads_gpo_list()` resolves a SAM account and computes applicable GPOs with user or machine token context. `net_ads_gpo_link_get()` reads `gPLink`; `net_ads_gpo_link_add()` writes a link. `linkdelete` exists but is disabled.

Control flow: commands validate arguments, allocate a talloc context, call `ads_startup()`, call one libgpo/libads helper, dump GPO/link structures, and free context. The list path checks `UF_WORKSTATION_TRUST_ACCOUNT` to choose `GPO_LIST_FLAG_MACHINE` plus `gp_get_machine_token()`; users use `ads_get_sid_token()`.

State and persistence: list/get operations are read-only LDAP/GPO queries. `linkadd` mutates a container's GPO link attribute. No local persistent state is written.

Dependencies/integration: depends on `ads_startup()` from `net_ads.c`, libgpo headers/prototypes, ADS helpers, and AD flags. Reached through the `net ads gpo` entry in `net_ads.c`.

Risks: accepts raw DNs/GPO names and relies on caller escaping. Several failures flow to `out` but still return `0`, so status may not signal errors. DACL reads require sufficient permissions. Disabled delete support suggests incomplete link lifecycle coverage.

Test signals: list all GPOs; list applicable GPOs for user and machine; get by DN and name; add link then read it back; malformed DN and insufficient-permission cases; exit-code checks on failures.
