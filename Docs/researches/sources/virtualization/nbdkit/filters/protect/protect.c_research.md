# File Research: sources/virtualization/nbdkit/filters/protect/protect.c

This filter prevents modifications to configured byte ranges unless the requested write would leave protected bytes unchanged. `protect=START-END` adds a protected inclusive range; `protect=~START-END` protects everything except the specified range by adding up to two complementary ranges. Empty starts and ends mean beginning of file and `INT64_MAX`.

During config completion, ranges are sorted and adjacent/overlapping ranges are merged, then converted into a complete `regions` table spanning the 64-bit address space with protected and unprotected regions. Protected regions carry non-NULL data in the region union; unprotected regions do not.

`check_write` walks the affected regions for a write-like request. For protected spans it reads the current backend bytes and compares them to the proposed write buffer, or checks that the current bytes are already zero for trim/zero operations. If the request would alter protected data, it fails with `EPERM`; otherwise the write, trim, or zero is forwarded.

The design allows idempotent writes and zero/trim over already-zero protected data. Its cost is read-before-write overhead on protected regions. Pointer arithmetic on `buf` advances even when `buf == NULL`; this is tolerated by the compiler in this code path but is a portability-sensitive C idiom.
