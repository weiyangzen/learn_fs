# File Research: sources/virtualization/nvme-cli/nvme.h

- Purpose: central nvme-cli header for global arguments, output flags, helper macros, and shared command/open declarations.
- Output model: defines `nvme_print_flags` values `NORMAL`, `VERBOSE`, `JSON`, `VS`, `BINARY`, and `TABULAR`.
- Global args: `struct nvme_args` carries output format, verbosity, timeout, dry-run, retry/probing toggles, and output format version.
- CLI macro: `NVME_ARGS` appends common global options to command-specific argconfig option arrays.
- Topology helpers: includes multipath detection and iopolicy table-column filtering helpers.
- Core declarations: exposes `parse_and_open`, transport cleanup, output format validation, `__id_ctrl`, `libnvme_strerror`, elapsed time helper, register helpers, and `nvme_get_nsid_log`.
- Cleanup integration: defines `__cleanup_nvme_transport_handle` for automatic transport handle release.
