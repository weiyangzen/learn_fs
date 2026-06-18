# File Research: sources/local-fs/udftools/wrudf/ide-pc.h

## Purpose

`ide-pc.h` is the ATAPI/MMC command interface header used by `wrudf` for CD/DVD media access. It declares packed-ish C structures matching SCSI/MMC response and mode-page layouts, constants for disc/session/write modes, and function prototypes implemented by the lower-level `ide-pc.c` command layer outside this group.

## Main Definitions

The header defines device and media inquiry structures:

- `struct cdrom_inquiry` for SCSI INQUIRY data, including peripheral type constants `INQ_WORM` and `INQ_CDROM`.
- `struct cdrom_discinfo` for READ DISC INFORMATION, with disc/session status constants such as `DS_EMPTY`, `DS_APPENDABLE`, `DS_COMPLETE`, `SS_EMPTY`, `SS_APPENDABLE`, and `SS_COMPLETE`.
- `struct cdrom_trackinfo` for READ TRACK INFORMATION, carrying flags such as `fixpkt`, `packet`, `blank`, `rsrvd_trk`, next-writable-address validity, fixed-packet size, and track size.
- `struct cdrom_buffercapacity`, `struct cdrom_reccapacity`, and `struct cdrom_header` for buffer capacity, recorded capacity, and sector header reads.

It also declares MODE SENSE/SELECT page layouts:

- `mode_hdr` for the mode parameter header.
- `struct read_error_recovery_params` for the read/write error recovery page.
- `struct cdrom_cacheparams` for cache-control settings.
- `struct cdrom_writeparams` for write parameters, including write type, packet/fixed-packet selection, multisession mode, data block type, packet size, MCN/ISRC fields, and XA subheader bytes.
- `struct cdrom_capabilities` for CD/DVD read/write capability and mechanical status.

## Command Surface

The prototypes expose the command operations used by the wrudf code:

- Drive/media control: `blank`, `format`, `close_track_session`, `synchronize_cache`, `test_unit_ready`, `getDriveState`, `mediumRemoval`, `startStopUnit`, `set_cdspeed`.
- Metadata reads: `inquiry`, `read_discinfo`, `read_trackinfo`, `read_buffercapacity`, `read_reccapacity`, `read_header`.
- Data I/O: `readCD`, `writeCD`, and `verify` with an `MMC2`-dependent signature.
- Mode pages: `mode_sense`, `mode_select`, `get_writeparams`, `set_writeparams`, and `get_capabilities`.
- Error reporting: `fail`, `get_sense_data`, and `get_sense_string`.

## Role In This Group

`wrudf-cdrw.c` uses the disc/track/mode-page structures to classify media as CD-R or CD-RW, validate fixed-packet requirements, set write parameters, tune error recovery, and read/write packets. `wrudf-cdr.c` uses buffer-capacity and track-info calls for append-style CD-R writing and next-writable-address management. `wrudf.c` and command code rely on these wrappers indirectly through the I/O layer.

## Notable Details

The structures use implementation-defined bitfields and host integer types such as `u_int` and `u_short`, so their binary layout is compiler and endian sensitive. The surrounding code assumes Linux/GCC-style layout and often uses direct struct reads from device command buffers.

Several comments use C++ `//` comment syntax in a C header, so the code assumes a C99-or-compiler-extension build mode.
