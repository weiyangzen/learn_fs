# File Research: sources/local-fs/dlm/dlm_sand/dlm_sand_sock.h

This header defines the local socket protocol for `dlm_sand`.

Key constants:
- Control socket path: `DLM_SD_SOCK_PATH` = `dlm_sd_sock`.
- Query socket path: `DLM_SDQ_SOCK_PATH` = `dlm_sd_query_sock`.
- Magic: `DLM_SD_MAGIC` = `0x20240307`.
- Version: `DLM_SD_VERSION` = `0x00010001`.
- Control commands: reload config and set config.
- Query commands: dump status, dump config, dump debug.
- Dump size: `DLM_SD_DUMP_SIZE` = 1 MiB.

Main structure:
- `struct dlm_sd_header` contains magic, version, command, option, length, flags, integer data, padding field named `unsued`, and a name buffer sized `DLM_LOCKSPACE_LEN + 8`.

Important dependencies:
- Requires `DLM_LOCKSPACE_LEN` from DLM constants through include context.
- Consumed by `dlm_sand` main/query/control code outside this file list.

Notable detail:
- The field name `unsued` is misspelled but part of the C struct layout; changing it is source-visible even though layout would remain identical.
