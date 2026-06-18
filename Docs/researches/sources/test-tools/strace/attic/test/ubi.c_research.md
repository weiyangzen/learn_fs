<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/ubi.c -->
# sources/test-tools/strace/attic/test/ubi.c

Purpose: ioctl decoder exerciser for UBI userspace API commands and structures.

Important data/types: initializes `ubi_mkvol_req`, `ubi_rsvol_req`, `ubi_rnvol_req`, `ubi_attach_req`, `ubi_map_req`, `ubi_set_vol_prop_req`, and a large `uint64_t bytes` value. Issues create, resize, rename, attach, volume update, eraseblock map/unmap/status/change, property set, remove, and detach ioctls against `/dev/null`.

Control flow: fixed sequence of ioctl calls, including a zeroed property structure after one populated call.

State and persistence: no intended UBI device changes because fd is `/dev/null`; syscall argument decoding is the test output.

Dependencies and integration: requires `<mtd/ubi-user.h>` and strace UBI ioctl decoders.

Risks: some structures (`attach`, `map`, `rnvol` padding) are partly uninitialized, intentionally broadening decoded data but making output nondeterministic. Header availability varies. Test signals: strace should print symbolic UBI ioctl names and nested structure fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/ubi.c -->
