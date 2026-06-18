# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/smp_transport.h

This header defines the kernel SMP transport abstraction for SAS expander/SMP devices.

Key definitions:
- Defines SMP device properties: `smp-device`, `smp-wwn`, and `report-manufacturer`.
- Defines `smp_address_t` containing expander WWN and transport vector.
- Defines `smp_device_t` containing SMP address, devinfo pointer, HBA-private pointer, and target-private pointer.
- Defines `smp_pkt_t` with request/response buffers and sizes, timeout, errno-style completion reason, and retry indication.
- Defines `smp_hba_tran` transport vector with HBA private data and `init`, `free`, and `start` callbacks.
- Declares HBA/iport setup and teardown APIs.
- Declares target/framework APIs `smp_probe()` and `smp_transport()`.
- Declares private SMP device property get/lookup/update/remove/free helpers.

Dependencies:
- Includes `sys/types.h` and `sys/scsi/impl/usmp.h`.
- Kernel content is gated by `_KERNEL`.

Impact:
- Provides the transport/framework bridge for issuing SMP requests to SAS expanders and managing SMP child devices.

Cautions:
- `smp_pkt_reason` is described as a code from `errno.h`, not an SMP result code.
- Property helper flags are simplified compared with `scsi_device` property helpers and only model device-node properties.
