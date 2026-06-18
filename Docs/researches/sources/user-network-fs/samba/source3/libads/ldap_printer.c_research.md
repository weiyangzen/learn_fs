# sources/user-network-fs/samba/source3/libads/ldap_printer.c

## Purpose

`ldap_printer.c` publishes and locates AD `printQueue` objects for Samba printers. It bridges spoolss RPC printer metadata and ADS LDAP add/modify operations.

## Important APIs, Types, and Functions

Public functions are `ads_find_printer_on_server`, `ads_find_printers`, `ads_mod_printer_entry`, `ads_add_printer_entry`, and `get_remote_printer_publishing_data`. Mapping helpers `map_sz`, `map_dword`, `map_bool`, `map_multi_sz`, and `map_regval_to_ads` translate `struct registry_value` data into an `ADS_MODLIST`. The static `valmap_to_ads` table maps many `SPOOL_REG_*` registry names to AD attribute updates.

## Control Flow

`ads_find_printer_on_server` first locates the server machine account, extracts its DN/CN, then searches for a printer named `servercn-printer` with full attributes and `nTSecurityDescriptor`. `ads_find_printers` searches visible `printQueue` entries with UNC names. Add/modify wrappers delegate to `ads_gen_add` and `ads_gen_mod`, adding `objectClass=printQueue` for creates.

`get_remote_printer_publishing_data` opens the remote printer over spoolss, enumerates `DsDriver` and `DsSpooler` printer data keys, maps each returned registry value into LDAP modifications, adds the printer name, closes the policy handle, and returns the last spoolss status.

## State and Persistence Behavior

This file owns no durable local state. It reads remote spooler registry state and writes AD printer object attributes through LDAP modifications. Temporary printer names, mod lists, and enum results are caller/talloc owned.

## Dependencies and Integration Points

Dependencies include `ads.h`, OpenLDAP result helpers, spoolss RPC client helpers, registry value parsers, and spooler registry constants. It integrates with printer publishing workflows in `net ads`/Samba print serving and relies on `ldap.c` for search and modify operations.

## Risks and Test Signals

Risks include malformed server DNs, printer names requiring LDAP escaping, partial publication when one spoolss key fails but another succeeds, type mismatches in registry values, boolean values encoded as one-byte `REG_BINARY`, and silently ignored unmapped attributes. Tests should cover locating printers by server CN, publishing a representative mix of REG_SZ/REG_DWORD/REG_BINARY/REG_MULTI_SZ values, failed spoolss open/enum paths, AD add versus modify, and cleanup of LDAP/RPC resources.
