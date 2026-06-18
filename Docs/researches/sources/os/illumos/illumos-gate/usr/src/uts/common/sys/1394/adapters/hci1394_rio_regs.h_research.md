# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_rio_regs.h

This header defines Sun RIO chipset vendor-specific OpenHCI register mapping and bitfields.

Key contents:
- Register-set mapping: base `0x2`, offset `0x0`, length `0x800`.
- RIO pass-1 GUID setup constants, including Sun OUI and GUID masks.
- Vendor register offsets for interrupt event/mask, DMA burst size, transmit control, host control, and statistics registers.
- Interrupt bits for stats counters and link-on.
- Burst-size field masks/shifts and values for 32/64/128/256 byte bursts.
- Transmit boundary and host-control bits.
- `RIOREG_HOST_CONTROL_SETTING` enables descriptor prefetching across AT, IT, AR, and IR engines.
- Statistics masks for retries, errors, bus errors, and physical read/write queues.

Use is through `hci1394_vendor_reg_read()` and `hci1394_vendor_reg_write()`.
