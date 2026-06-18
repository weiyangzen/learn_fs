# File Research: sources/windows/winbtrfs/src/shellext/mappings.cpp

Read status: complete, 338 lines.

This file implements a standalone mappings dialog for viewing WinBtrfs UID and GID registry mappings.

Key behavior:
- Reads UID mappings from `SYSTEM\\CurrentControlSet\\Services\\btrfs\\Mappings`.
- Reads GID mappings from `SYSTEM\\CurrentControlSet\\Services\\btrfs\\GroupMappings`.
- Registry value names are expected to be SID strings; values are `REG_DWORD` UID/GID numbers.
- Converts SID strings to `PSID` with `ConvertStringSidToSidW`.
- Resolves SIDs to domain/name display values using LSA policy lookup and `LsaLookupSids`.
- Displays mappings in a list view with a tab control switching between UID and GID mappings.
- Exported `MappingsTest` sets DPI awareness and opens the dialog.

Implementation structure:
- Uses small RAII deleters for LSA handles, LSA allocated pointers, registry keys, and local SID allocations.
- `mapping_entry` owns the SID, numeric value, resolved domain/name, and SID use.
- `populate_list` refreshes the list for the selected tab.
- `init_dialog` creates tabs and list columns, then populates the initial view.
- `MappingsDlgProc` handles init, OK/cancel, and tab selection changes.

Integration:
- Depends on shared `module`, `load_string`, `error_message`, and `set_dpi_aware`.
- Uses resource IDs for the dialog, tabs, and list column labels.
- Not tied to COM factory creation; it is an exported rundll-style utility entry.

Risk and maintenance notes:
- The registry open path throws if the mappings key does not exist. If absence is normal, the UI may need an empty-list path.
- Entries whose value type is not `REG_DWORD` are skipped.
- The code ignores unconvertible SID strings.
