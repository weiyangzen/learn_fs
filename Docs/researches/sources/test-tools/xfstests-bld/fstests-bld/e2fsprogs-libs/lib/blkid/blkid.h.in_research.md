# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkid.h.in

Purpose: public libblkid API template installed as `blkid/blkid.h`.

Important APIs/types/functions: exposes opaque handles `blkid_dev`, `blkid_cache`, iterators, `blkid_probe`, and `blkid_topology`; defines `blkid_loff_t` as `__s64`; declares version constants and flags for `blkid_get_dev`. Public APIs cover cache lifetime, device iteration/search, device number resolution, full probing, size detection, verification, tag lookup/iteration/parsing, topology probing, and version parsing.

State and persistence: public callers receive handles to internal cache/device state. Cache persistence is controlled by `blkid_get_cache`/`blkid_put_cache`, with on-disk cache behavior implemented elsewhere.

Dependencies and integration: includes `sys/types.h` and generated `blkid_types.h`. Used by applications, `blkidP.h`, and e2fsprogs utilities.

Risks and test signals: ABI stability depends on keeping structs opaque and type widths correct. Test C/C++ inclusion, all public prototypes, flag semantics, and interaction with generated `blkid_types.h`.
