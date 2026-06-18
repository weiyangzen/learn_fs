# File Research: sources/local-fs/udftools/cdrwtool/cdrwtool.c

Implements low-level MMC/SCSI CD/DVD writer operations through Linux `CDROM_SEND_PACKET` ioctls.

Main capabilities:
- Build and send generic packet commands with optional request-sense reporting.
- Poll `TEST_UNIT_READY` after long operations and report progress from sense data.
- Read and set write-parameter mode pages.
- Write blocks with `GPCMD_WRITE_10`.
- Blank rewritable media.
- Format media using modern FORMAT UNIT code 1, with fallback to legacy code 7.
- Read disc and track/rzone information.
- Reserve tracks, close tracks, and close sessions.
- Read drive buffer capacity.
- Set CD write speed.
- Lock/unlock drive door and validate media status.
- Print disc/track/write-parameter summaries.

Important helpers:
- `wait_cmd_sense` and `wait_cmd` centralize packet ioctl setup.
- `wait_for_unit_ready` handles long blank/format/close completion.
- `set_write_mode` edits mode page 5 fields from `write_params_t`.
- `make_write_page` translates `struct cdrw_disc` CLI settings into write mode fields.
- `cdrw_init_disc` sets defaults: fixed packets, 32-block packets, mode 2, speed 12x.

Dependencies:
- Linux CD-ROM headers and ioctls.
- Endian helpers from `libudffs.h`.
- Shared `struct cdrw_disc` and `write_params_t` from `cdrwtool.h`.

Notable quirks:
- `get_write_mode` reconstructs only one byte of `packet_size` from the four-byte mode-page field.
- Fixed-packet file tail padding uses `memset(&buf[ret], 0, size - ret - 1)`, leaving one byte outside the zero-fill range.
- Numeric device/media inputs are trusted after parsing; most validation relies on the drive rejecting invalid packet commands.
