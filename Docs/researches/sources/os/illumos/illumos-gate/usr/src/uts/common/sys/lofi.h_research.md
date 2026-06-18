# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lofi.h

## Role

Loopback file block-device (`lofi`) ioctl ABI and kernel state header, including support for compressed and encrypted lofi images.

## Structure

- Defines device/node names for `/dev/lofictl`, block lofi devices, and raw lofi devices.
- Defines compression constants, partition/minor conversion macros, and private lofiadm ioctl usage.
- Defines `iv_method_t`, `struct lofi_ioctl`, ioctl command numbers, and file/vnode type eligibility macros.
- Defines crypto metadata offset/magic/version and, under `_KERNEL`, compressed segment cache entries, compression buffers, crypto metadata, and the large `struct lofi_state`.
- Defines compression function signature, compression info table structure, and known compression algorithm indexes.

## Dependencies And Consumers

Includes time, taskq, dkio, vnode, list, crypto API, and zone headers; kernel builds include cmlb and open headers. Userland `lofiadm(8)` uses the private ioctl structure; the lofi driver uses the kernel-only state.

## Important Details

The comments call the ioctls private and for `lofiadm(8)`. Forced unmap can close the backing vnode while busy and cause later operations to see `DKIO_DEV_GONE`; cleanup unmap defers teardown until last close. `struct lofi_ioctl` embeds fixed-size path, algorithm, cipher, and key buffers, so ABI size matters.

## Research Notes

Read completely: 342 lines, 10807 bytes.
