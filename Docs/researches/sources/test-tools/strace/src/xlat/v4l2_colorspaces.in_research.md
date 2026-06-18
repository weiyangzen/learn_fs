# sources/test-tools/strace/src/xlat/v4l2_colorspaces.in

Purpose: `v4l2_colorspaces.in` is a strace xlat input table for V4L2 constants. The xlat generator turns these rows into C lookup data so syscall decoders can print symbolic names instead of raw integers for this kernel ABI surface. Source provenance is `include/uapi/linux/videodev2.h`, and the declared prefix is `V4L2_COLORSPACE_`.

Important APIs/types/functions: this file has no executable functions; its API is the xlat mini-language consumed by strace's build tooling. Directives seen here are `#unconditional`, `#value_indexed`, `#From include/uapi/linux/videodev2.h`, `#Prefix V4L2_COLORSPACE_`. Generation behavior is `#unconditional`, `#value_indexed`. Representative constants are `V4L2_COLORSPACE_DEFAULT`, `V4L2_COLORSPACE_SMPTE170M`, `V4L2_COLORSPACE_SMPTE240M`, `V4L2_COLORSPACE_REC709`, `V4L2_COLORSPACE_BT878`, `V4L2_COLORSPACE_470_SYSTEM_M`, `V4L2_COLORSPACE_470_SYSTEM_BG`, `V4L2_COLORSPACE_JPEG`, ... (13 total), `V4L2_COLORSPACE_BT2020`, `V4L2_COLORSPACE_RAW`, `V4L2_COLORSPACE_DCI_P3`.

Control flow: at build time, strace's xlat generation includes this `.in` file, interprets directives, evaluates the listed macros or explicit values against bundled/system headers, and emits a decoder table. At runtime, syscall-specific printers consult that generated table when decoding V4L2 arguments, flags, attributes, ioctl values, socket options, or netlink fields.

State/persistence behavior: the file is static source data and stores no runtime state. Persistence is through the generated C/header artifacts in the build tree; correctness depends on keeping the table synchronized with upstream UAPI definitions and preserving row ordering when `#sorted` or explicit values are present.

Dependencies: primary dependency is `include/uapi/linux/videodev2.h` plus the strace xlat generation scripts and compatibility headers. Prefix handling (`V4L2_COLORSPACE_`) controls printed-name normalization.  The value-indexed directive means consumers can use dense numeric lookup when the generated C table is emitted. `#unconditional` keeps these constants visible even when host headers do not expose the exact macro set.

Integration points: integrated by syscall decoders that include the generated xlat for V4L2. Common integration surfaces in this group include ioctl decoders, netlink attribute decoders, socket option printers, memory-management/syscall flag printers, signal/prctl/perf/KVM/io_uring/V4L2 paths, and architecture-specific decoders.

Risks: stale constants, wrong explicit numeric values, accidental prefix drift, or broken sort/value-indexing directives would produce misleading strace output without changing traced program behavior. Host-header variability is also a risk for rows without `#unconditional`.

Test signals: useful checks are rebuilding generated xlat artifacts, running strace's decoder tests that exercise the relevant syscall family, comparing printed symbolic names against kernel UAPI headers, and verifying unknown-bit fallback output. This file has 17 source lines, 13 data rows, and value style: All 13 rows name constants without local values, so the generated xlat relies on the included header definitions. Inline category comments: none.
