# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/stdef.h

## Purpose
Private definition header for the SCSI tape target driver, covering drive types/options, mode pages, density/log/tape-alert data, tape positioning, recovery metadata, soft-state, reservations, timeouts, debug macros, and media/error thresholds.

## Main Interfaces
- Tape drive type constants mapped to `mtio.h` values.
- Stable drive option flags such as variable block, QIC/reel, backspace support, buffered writes, compression, reserve/release behavior, WORM, cleaning bit variants, and valid option mask.
- Log page and TapeAlert constants/enums.
- `struct st_drivetype`: configured drive identity, block size, options, retries, density/media tables, and command timeouts.
- Mode page layouts: compression, device configuration, SAS LUN, sequence mode, report supported operation codes, report density support, read block limits.
- Position types and structures: `tapepos_t`, short/long/extended READ POSITION data, `read_pos_data_t`.
- Command attribute and recovery structures.
- `struct scsi_tape`: main tape soft-state with SCSA device, queues, special buffers, mode data, drive table, position, state, retry/throttle, media state, RQS, reservations, error stats, x86 contiguous memory, recovery taskq, unit attention, multipath, and TLR state.
- Reservation flags and persistent reservation service action constants.
- Timeout/retry constants and SPACE command encoding macros.

## Dependencies And Relationships
Includes DDI, synchronization, kstat, SCSI types, generic sense, `mtio.h`, and taskq headers. Uses `struct scsi_pkt`, `struct uscsi_cmd`, SCSA watch tokens, and tape ioctl/minor semantics.

## Research Notes
The header supports both legacy and logical tape positioning, several bitfield layouts for different host endianness, and a large amount of historical drive behavior compatibility.

## Notable Risks
- Drive option flag values are explicitly stable and must not be renumbered.
- SPACE command encoding depends on `size_t` width.
- Tape position recovery, filemark/EOM state, and WORM/write-protect behavior are correctness sensitive.
- Bitfield protocol structures depend on `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`.
