# sources/user-network-fs/samba/source3/param/service.c

Purpose: resolves requested SMB share/service names into loadparm service numbers, including dynamic registry shares, `[homes]`, printers, usershares, default service fallback, and local address filtering.

Important APIs and flow: `find_service()` copies and normalizes the requested name, checks loaded services, tries registry shares before dynamic homes, maps usernames if needed, creates home services through `add_home_service()`, creates printer services when printcap says the name is valid, loads usershares after lowercasing, and finally recurses through `default service` if safe. `load_registry_service()` and `load_registry_shares()` wrap registry-backed loadparm APIs. `lp_allow_local_address()` compares a local socket address against configured `server addresses`.

State and persistence: modifies global loadparm service state by adding homes/printers/usershares and by processing registry shares. It reads passwd/home data, printer lists, usershare files, and registry smbconf through loadparm.

Dependencies and integration: used by smbd connection setup. Depends on loadparm, printer list, username mapping, tsocket normalization, passdb SID lookup includes, and auth utilities.

Risks: order matters: explicit registry shares intentionally beat home-directory autoloading. Default-service recursion must block special services and path traversal. Usershare lookup lowercases the name in place. `lp_allow_local_address()` ignores malformed configured addresses after logging, which can make partial lists permissive only for remaining valid entries.

Test signals: requested share resolution for explicit shares, registry shares, domain-qualified home names, mapped usernames, printers, usershares, default service fallback, invalid snums, and IPv4/IPv6 server address normalization.
