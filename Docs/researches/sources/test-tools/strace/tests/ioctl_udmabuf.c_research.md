<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_udmabuf.c -->
# sources/test-tools/strace/tests/ioctl_udmabuf.c

Purpose: Tests decoding of `UDMABUF_CREATE` and `UDMABUF_CREATE_LIST` ioctl arguments for single and list-based DMA buffer creation.

Important APIs/types/functions: Uses `<linux/udmabuf.h>`, `struct udmabuf_create`, `struct udmabuf_create_list`, `struct udmabuf_create_item`, `ioctl`, `skip_if_unavailable`, and strace `strval32`/`strval64` fixtures.

Control flow: `main` verifies `/proc/self/fd/` availability, then `test_create` checks NULL and four populated `udmabuf_create` combinations. `test_create_list` allocates a variable-length structure sized with `offsetof(..., list)` plus four list entries, fills list items, varies top-level flags, and prints nested item arrays.

State/persistence behavior: It only reads `/proc/self/fd/` availability and uses fd `-1`, so there are no persistent kernel objects. The apparent fd `0</dev/null>` text is expected strace fd-path rendering, not a new persistent resource.

Dependencies: Requires a kernel header exposing UDMABUF ioctl structs and flags. It relies on strace test helpers for tail allocation and return formatting.

Integration points: Covers ioctl decoders that print memfd arguments with fd paths, flag xlat output for `UDMABUF_FLAGS_CLOEXEC`, unsigned widening of negative offsets/sizes, and variable-length array decoding.

Risks: Header availability and struct layout are relatively new, and list count handling can over-read if the decoder ignores size/count boundaries. Raw versus symbolic flag output must remain stable.

Test signals: Output should show NULL handling, four single-create structures, four create-list structures with nested list entries, EBADF return strings, and the final exit marker.

Source read signal: complete file read for this research pass; file size 124 line(s), 3123 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_udmabuf.c -->
