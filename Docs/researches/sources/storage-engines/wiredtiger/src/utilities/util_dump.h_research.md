## sources/storage-engines/wiredtiger/src/utilities/util_dump.h

Purpose: declares the JSON dump format marker and version constants shared by dump and JSON load code.

Important APIs/types/functions: defines `DUMP_JSON_VERSION_MARKER` as `WiredTiger Dump Version`, `DUMP_JSON_CURRENT_VERSION` as `1`, and `DUMP_JSON_SUPPORTED_VERSION` as `1`.

Control flow: no executable flow. `util_dump.c` emits the marker/current version in JSON output; `util_load_json.c` requires the marker and rejects versions newer than supported.

State and persistence behavior: controls serialized JSON dump compatibility. Changing these constants changes the accepted or emitted on-disk/interchange dump format.

Dependencies and integration points: included by both JSON-producing dump code and JSON-consuming load code. It is part of the implicit file-format contract for `wt dump -j` and `wt load -j`.

Risks: bumping `DUMP_JSON_CURRENT_VERSION` without updating parser support will make fresh dumps unloadable by the same utility. Accepting a supported version without parser changes can misload data if structure changed.

Test signals: JSON dump/load round trips should assert the marker is present, current version is emitted, supported version is accepted, and a higher version is rejected with `ENOTSUP`.
