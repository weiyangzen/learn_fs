<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ubi.c -->
# sources/test-tools/strace/tests/ioctl_ubi.c

Purpose: Exercises decoding of UBI ioctl commands and UBI request structures, including no-argument commands, integer pointer commands, 64-bit integer pointer commands, and complex volume/eraseblock structures.

Important APIs/types/functions: Uses `ioctl`, `<mtd/ubi-user.h>`, `struct ubi_attach_req`, `ubi_leb_change_req`, `ubi_map_req`, `ubi_mkvol_req`, `ubi_rnvol_req`, `ubi_rsvol_req`, and `ubi_set_vol_prop_req`. Helpers `do_ioctl`, `do_ioctl_ptr`, optional `skip_ioctls`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `fill_memory`, `fill_memory_ex`, and `CLAMP` drive expected output construction.

Control flow: The program first handles optional fault-injection locking when `INJECT_RETVAL` is defined. It then tests no-arg UBI volume block ioctls, pointer-to-int commands, pointer-to-int64 commands, NULL and faulting pointers for structured requests, and filled valid structures for attach, LEB change, LEB map, make volume, rename volume, resize volume, and set volume property. Rename-volume coverage intentionally varies `count`, name length, embedded NUL bytes, and maximum-name boundary cases.

State/persistence behavior: The normal variant calls every ioctl on fd `-1`, so no UBI device state is touched. State is limited to deterministic in-memory request buffers and the global `errstr`. The success wrapper uses injected return values to exercise output-argument annotations such as updated UBI or volume ids without requiring a real device.

Dependencies: Depends on Linux UBI UAPI structs and constants, strace tail allocation helpers, and fault-injection test support when compiled through the success wrapper.

Integration points: Validates strace's UBI ioctl decoder, enum rendering for volume type, data type, flags, volume properties, string truncation, array decoding, NULL/fault pointer handling, and ioctl number clash reporting for a legacy `NET_REMOVE_IF` value.

Risks: UBI UAPI changes can add fields or constants. Name-length handling is easy to regress because the decoder must avoid reading beyond fixed UAPI limits while preserving ellipsis behavior. Injected-success output must stay synchronized with strace fault-injection semantics.

Test signals: Expected lines include decoded UBI structures, unknown `dtype`, volume-name truncation, `=>` result fields on injected success, and `+++ exited with 0 +++`.

Source read signal: complete file read for this research pass; file size 303 line(s), 8906 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ubi.c -->
