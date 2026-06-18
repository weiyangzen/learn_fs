# Research: sources/storage-engines/rocksdb/include/rocksdb/unique_id.h

- **Purpose:** Declares helpers for deriving stable binary unique IDs for SST files from `TableProperties`.
- **Important APIs/types/functions:** `GetUniqueIdFromTableProperties()` returns a 128-bit binary ID, `GetExtendedUniqueIdFromTableProperties()` returns a 192-bit binary ID, and `UniqueIdToHumanString()` formats binary IDs as uppercase hex groups separated by dashes.
- **Control flow:** Callers pass parsed table properties; helpers return `NotSupported` when required properties are missing, typically for older SSTs. Successful IDs can be stored, compared, shortened as prefixes, or displayed using the formatter.
- **State and persistence:** The ID is derived from persisted SST properties such as DB/session/file identity. The binary string may contain NUL bytes and must not be handled with C-string APIs.
- **Dependencies:** Depends on `table_properties.h` and `Status`.
- **Integration points:** Backup systems, file catalogs, and diagnostics use these IDs to distinguish SST files beyond file number/name.
- **Risks:** Older files do not support IDs. Misusing `.c_str()` loses entropy at embedded NUL bytes. 128-bit IDs are sufficient for most deployments, but globally shared backup namespaces may need the 192-bit extended form.
- **Test signals:** Tests should cover supported and unsupported property sets, binary length, non-zero 128-bit prefix, human formatting of full and prefix IDs, and collision assumptions using DB/session/file changes.
