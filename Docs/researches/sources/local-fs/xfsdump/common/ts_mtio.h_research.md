# File Research: sources/local-fs/xfsdump/common/ts_mtio.h

## Role

This header carries SGI/IRIX-style magnetic tape ioctl compatibility definitions used by xfsdump tape support.

It supplements Linux `<sys/mtio.h>` with historical tape operation codes, status structures, capability flags, and vendor-specific tape command structures.

## Operation Codes

The header aliases and defines tape operation subcodes for:

- retention
- reserve/release/persistent reservation operations
- append-to-file behavior
- setmark skipping
- audio/data mode switching
- SCSI-specific special operations
- legacy ABI operation mappings

## Status Structures

Defined status/accounting structures include:

- `mtget_sgi`
- `old_mtget`
- `mt_prsv`
- `mtgetext_t`
- `mtacct_t`
- `mtvid`
- `mtblkinfo`

These provide tape status, position, residuals, partition information, capabilities, byte/read/write counters, persistent reservation state, and block-size metadata.

## SCSI And Audio Structures

The header defines structures for SCSI log reads, audio DAT positioning/timecode, drive capability reporting, front-panel messages, vendor-specific position payloads, and tape attributes.

Audio support includes BCD timecode fields and positioning modes for program, absolute, running, and program-relative time.

## Ioctl Numbers

`MTIOCODE()` constructs ioctl numbers. The header defines many SGI-style ioctls such as:

- `MTIOCGET_SGI`
- `MTIOCGETBLKSIZE`
- `MTSCSIINQ`
- `MTSPECOP`
- `MTIOCGETBLKINFO`
- `MTANSI`
- `MTCAPABILITY`
- `MTSETAUDIO`
- `MTGETAUDIO`
- `MTSCSI_SENSE`
- `MTSCSI_RDLOG`
- `MTIOCGETEXT`
- `MTACCT`
- `MTSETVID`
- `MTPRSV`

## Capability And Status Flags

The file defines drive position/status bits, error-register bits, and many `MTCAN_*` capability bits covering backspacing, append, setmarks, partitions, media removal, sync, EOD handling, variable/fixed block sizes, density/speed, compression, fast seek, load behavior, and audio support.

## User Request Codes

The final section defines `MTR_*` request codes used in extended tape status to identify the last user request, including read, write, filemark operations, seeking, erase, unload, persistent reservation operations, load, and filemark-positioning variants.

## Compatibility Nature

This header is primarily a compatibility surface for old SGI tape-driver behavior. Much of it documents device-specific or historical behavior that xfsdump's tape paths may still need to compile against.
