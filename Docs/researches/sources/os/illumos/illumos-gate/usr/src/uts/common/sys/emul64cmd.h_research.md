# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64cmd.h

This header defines per-command private data and command flags for the `emul64` SCSI adapter emulator driver.

Key contents:
- Packet/private-data conversion macros:
  - `PKT2CMD(pkt)`
  - `CMD2PKT(sp)`
- `struct emul64_cmd`: per-command state allocated with `scsi_pkt`, including packet pointer, queue link, buffer address, completion deadline, flags, byte count, CDB/SCB lengths, and owning `emul64` instance pointer.
- Command flags:
  - `CFLAG_FINISHED`
  - `CFLAG_COMPLETED`
  - `CFLAG_IN_TRANSPORT`
  - `CFLAG_TRANFLAG`
  - `CFLAG_DMAVALID`
  - `CFLAG_DMASEND`
  - `CFLAG_CMDIOPB`
  - `CFLAG_FREE`
  - `CFLAG_DMA_PARTIAL`

Dependencies:
- Includes `sys/scsi/scsi_types.h`.
- Depends on `struct scsi_pkt` and forward-declared `struct emul64`.
- Uses C++ guards.

Research notes:
- This is driver-private SCSI transport bookkeeping, not a general user ABI.
- The flags separate transport lifecycle state from DMA and allocation/free-list state.
- Storage relevance is direct to the emulated SCSI HBA path used for block-device testing.
