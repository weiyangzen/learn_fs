# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcid.h

Common CID/CMap data header. It defines `gs_cid_system_info_t` with `Registry`, `Ordering`, and `Supplement`, plus public GC descriptor macros for individual values and arrays. It also documents and declares null-CIDSystemInfo handling: a null value is represented by empty Registry/Ordering strings and Supplement zero, with helpers `cid_system_info_set_null` and `cid_system_info_is_null`.

This file is a small shared type contract used by CID-keyed font and CMap code. It depends on `gsstype.h` for `gs_const_string`.
