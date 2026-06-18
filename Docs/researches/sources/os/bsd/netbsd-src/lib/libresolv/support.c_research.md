# File Research: sources/os/bsd/netbsd-src/lib/libresolv/support.c

Read completely: 347 lines.

Contains support routines for the DST key subsystem. It verifies string prefixes while advancing parse pointers, computes significant bit counts, calculates DNS key ids/checksums, reads and writes unaligned 16/32-bit network-order integers, and builds/sizes DST key filenames.

`dst_s_build_filename()` creates `K<name>+<alg>+<id>.<suffix>` names while rejecting slash, backslash, and colon. `dst_s_fopen()` prepends the global `dst_path` and optionally applies permissions after opening.

The debug dump helper prints base64 or short length information when enabled. The file is small but central to DST file parsing and DNS KEY id compatibility.
