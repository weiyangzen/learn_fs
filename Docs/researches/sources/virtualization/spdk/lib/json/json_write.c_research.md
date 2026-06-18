# File Research: sources/virtualization/spdk/lib/json/json_write.c

Full-file read: 873 lines.

This file implements SPDK’s buffered JSON writer.

Main responsibilities:
- Manage `spdk_json_write_ctx` with callback, flags, indentation state, failure state, and a 4096-byte buffer.
- Emit scalar JSON values, names, arrays, objects, batches, UUIDs, byte arrays, raw values, formatted strings, and named variants.
- Escape UTF-8 and UTF-16LE strings into valid JSON, using short escapes or `\uXXXX`/surrogate pairs.
- Buffer output and flush through caller-provided write callbacks.
- Replay parsed `spdk_json_val` token trees via `spdk_json_write_val`.

Important control flow:
- `begin_value` handles comma/newline/indent emission and first-value state.
- `emit` fast-paths into the internal buffer; `emit_buf_full` flushes and recurses for overflow.
- `spdk_json_write_array_begin/object_begin` reset first-value state and increment indent.
- `spdk_json_write_name_raw` writes a name and colon, then allows the next value as first in that name context.
- `spdk_json_write_end` flushes, frees the context, and reports latched failure.

Integration points:
- Used by JSON-RPC responses, SPDK config emission, iSCSI info/config RPCs, and client request building.
- Depends on internal UTF helpers and SPDK string formatting helpers.

Risks and review notes:
- The writer has TODO comments for stricter container state checking; misuse can generate structurally invalid JSON.
- `emit_buf_full` uses pointer arithmetic on `void *`, relying on compiler behavior accepted in this codebase.
- Failure latching prevents silent success after callback or encoding failure.

Testing focus:
- Escaping all control characters and multibyte Unicode.
- Deep formatted arrays/objects.
- Callback failure propagation.
- Raw token replay for nested values.
