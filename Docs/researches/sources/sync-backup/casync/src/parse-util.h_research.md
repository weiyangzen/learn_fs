# sources/sync-backup/casync/src/parse-util.h

Purpose: declaration header for byte-size parsing/formatting helpers.

Important APIs/types/functions: defines `FORMAT_BYTES_MAX`, declares `parse_size(const char*, uint64_t*)`, and `format_bytes(char*, size_t, uint64_t)`.

Control flow/state: stateless API; callers own the output buffer for formatting and receive parsed values through an out-parameter.

Dependencies/integration: includes `<inttypes.h>` for `uint64_t`. The functions are suitable for command-line option parsing and diagnostic output across casync.

Risks/test signals: callers must provide buffers at least `FORMAT_BYTES_MAX` for conservative formatting. Input validation behavior is defined in the C file rather than documented in detail here.

Source research group: `subset-b-009122`.
