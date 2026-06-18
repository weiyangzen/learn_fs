# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadkio.h

## Scope

Complete file read, 236 lines. This header defines ioctl command numbers, command codes, error/status values, and request structures for the direct-coupled disk driver interface.

## Public Surface

It defines DIOCTL commands for geometry, physical geometry, model, serial, raw read/write command, and write-cache-enabled state. It conditionally defines `blkaddr_t`/`blkaddr32_t` like `dklabel.h`.

The ABI structures include:

- `dadk_ioc_string_t` and `_SYSCALL32` `dadk_ioc_string32_t`.
- `struct dadkio_derr`: driver error action/severity pair.
- `struct dadkio_status` and `_SYSCALL32` `struct dadkio_status32`.
- `struct dadkio_rwcmd` and `_SYSCALL32` `struct dadkio_rwcmd32`.

It defines direct command codes `DCMD_READ` through `DCMD_FLUSH_CACHE`, driver error codes `DERR_*`, raw read/write command codes, flags such as `DADKIO_FLAG_SILENT`, `DADKIO_ERROR_INFO_LEN`, and `DADKIO_STAT_*` status values.

## Behavior And Integration

This is a shared ioctl ABI used by disk drivers and user/kernel ioctl handlers. `dadkio_rwcmd` carries a command, flags, target block, user buffer, byte length, and status output. The 32-bit variants preserve compatibility for 32-bit processes on 64-bit kernels.

## Dependencies And Invariants

ABI correctness depends on fixed field widths, `_SYSCALL32` conversions, `blkaddr_t` selection, and the 128-byte additional error-info buffer. User pointers are represented as `caddr_t` or `caddr32_t`.

## Risks

The command namespace is old and mixes disk and CD-ROM operations. Callers must validate `buflen`, `bufaddr`, block range, direction, and status copyout carefully. `uint_t buflen` can be narrower than `size_t`, so large I/O requests must be bounded.
