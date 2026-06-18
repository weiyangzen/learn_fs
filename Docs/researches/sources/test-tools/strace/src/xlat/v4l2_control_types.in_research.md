# sources/test-tools/strace/src/xlat/v4l2_control_types.in

Purpose: `v4l2_control_types.in` is a strace xlat input table for V4L2 constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/videodev2.h`, and the declared prefix is `V4L2_CTRL_TYPE_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#unconditional`, `#sorted`, `#From include/uapi/linux/videodev2.h`, `#Prefix V4L2_CTRL_TYPE_`. Generation behavior is `#unconditional`, `#sorted`. Representative constants are `V4L2_CTRL_TYPE_INTEGER`, `V4L2_CTRL_TYPE_BOOLEAN`, `V4L2_CTRL_TYPE_MENU`, `V4L2_CTRL_TYPE_BUTTON`, `V4L2_CTRL_TYPE_INTEGER64`, `V4L2_CTRL_TYPE_CTRL_CLASS`, `V4L2_CTRL_TYPE_STRING`, `V4L2_CTRL_TYPE_BITMASK`, ... (40 total), `V4L2_CTRL_TYPE_AV1_TILE_GROUP_ENTRY`, `V4L2_CTRL_TYPE_AV1_FRAME`, `V4L2_CTRL_TYPE_AV1_FILM_GRAIN`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding V4L2 arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/videodev2.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`V4L2_CTRL_TYPE_`) controls printed-name normalization.  Lookup is by normal xlat entries rather than an explicitly value-indexed dense table. `#unconditional` keeps these constants visible even when host headers do not expose the exact macro set.

Integration points: integrated by syscall decoders that include the generated xlat for V4L2. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`. The sorted directive is a test signal: row order is intentional and should remain compatible with the requested sort.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 44 source lines, 40 data rows, and value style: All 40 rows name constants without local values, so the generated xlat relies on the included header definitions. Inline category comments: none.
