# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64.h

This header defines ioctl commands and payloads for the `emul64` SCSI adapter emulator test driver, mainly for manipulating large emulated device ranges and injecting errors.

Key contents:
- `EMUL64IOC` ioctl base.
- Ioctls:
  - `EMUL64_WRITE_OFF`
  - `EMUL64_WRITE_ON`
  - `EMUL64_ZERO_RANGE`
  - `EMUL64_ERROR_INJECT`
- Block range structure `emul64_range_t`.
- Target/LUN-specific range structure `emul64_tgt_range_t`.
- Error injection states:
  - `ERR_INJ_DISABLE`
  - `ERR_INJ_ENABLE`
  - `ERR_INJ_ENABLE_NODATA`
- Error injection payload `emul64_error_inj_data`, including target/LUN, injection state, sense data length, SCSI status, packet reason, and packet state.

Dependencies:
- Includes `sys/inttypes.h`, `sys/types.h`, and `sys/scsi/scsi.h`.
- Uses `diskaddr_t`, `struct scsi_status`, and SCSI packet status fields.
- Uses C++ guards.

Research notes:
- The file documents three original testing ioctls for ignoring writes, enabling writes, and zeroing ranges; the header also includes an error-injection ioctl.
- Storage relevance is direct for test infrastructure: it lets tests accelerate large-device operations or simulate SCSI behavior without real media changes.
