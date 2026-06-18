# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dump.h

Purpose: Defines the Emulex driver dump-file vocabulary: in-memory file buffers, dump event context, dump file sizes, dump types, segment identifiers, human-readable legends, dump regions, and dump table entry layouts.

Key definitions:
- `emlxs_file_t`: simple buffered file abstraction with `buffer`, current `ptr`, and `size`.
- `dump_temp_event_t`: links an HBA, temperature event type, and temperature value.
- File sizes: `EMLXS_TXT_FILE_SIZE`, `EMLXS_DMP_FILE_SIZE`, `EMLXS_CEE_FILE_SIZE`.
- Dump initiators: `DUMP_TYPE_USER`, `DUMP_TYPE_DRIVER`, `DUMP_TYPE_TEMP`.
- Dump output IDs: `DUMP_TXT_FILE`, `DUMP_DMP_FILE`, `DUMP_CEE_FILE`.
- Segment IDs cover firmware/HBA dump sections, SLI structures, PCI config, mailboxes, rings, buffer lists, revision info, HBA info, driver parameters, Solaris internal structures, config regions, CEE log, and non-volatile log.
- Legend strings map those segment IDs and subregions to printable labels.
- `DUMP_WAKE_UP_PARAMS` gives a display-oriented simplified wakeup parameter structure.
- `DUMP_TABLE_ENTRY_PORT_STRUCT`, `DUMP_TABLE_ENTRY_PORT_BLK`, and `DUMP_TABLE_ENTRY` model firmware dump-table entries with endian-sensitive bitfields.

Dependencies and interactions:
- Uses `struct emlxs_hba`, `DRIVER_NAME`, and `EMLXS_LITTLE_ENDIAN`.
- Extern prototypes for the dump implementation are in `emlxs_extern.h` under `DUMP_SUPPORT`.
- Dump state and per-HBA dump files are embedded in `emlxs_hba_t` in `emlxs_fc.h`.

Implementation notes:
- This is declarative only; it has no executable functions.
- The endian-sensitive table-entry bitfields are ABI-sensitive and must match firmware dump-table encoding.
- `CC_DUMP_USE_ALL_TABLES`, `CC_DUMP_FW_BUG_1`, and `CC_DUMP_ENABLE_PAD` are compile-time diagnostic/workaround switches.
