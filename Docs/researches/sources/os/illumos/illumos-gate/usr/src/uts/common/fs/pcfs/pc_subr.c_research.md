# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_subr.c

PCFS support routines for FAT timestamp conversion, long filename validation, and 8.3 name rendering.

Key responsibilities:
- Converts UNIX `timestruc_t` values to FAT date/time fields in `pc_tvtopct()`, enforcing the FAT 1980 to 2107 representable range.
- Converts FAT date/time fields back to 64-bit UNIX seconds in `pc_pcttotv()`, including fallback to the FAT epoch for impossible on-disk timestamps.
- Applies timezone adjustment through the PCFS seconds-west mount argument model, while explicitly not implementing daylight-saving correction.
- Validates long filename characters in UTF-8 or UTF-16 form through `pc_valid_lfn_char()` and `pc_valid_long_fn()`.
- Rejects reserved FAT long-name characters plus additional prohibited characters such as Yen sign and bidirectional override controls.
- Converts DOS filename and extension fields into printable `name.ext` strings through `pc_fname_ext_to_name()`, with optional case folding.

Dependencies:
- Uses PCFS label/dir/node headers, endian macros, Unicode validation, and kernel time/device support headers.
- Shares constants such as FAT date bit shifts, name limits, and valid character rules with the rest of pcfs.

Notable risks:
- FAT timestamp precision is two seconds and FAT access time only stores a date.
- Out-of-range UNIX times return `EOVERFLOW` on write-side conversion.
- The timezone state is global legacy state rather than obviously per-mounted filesystem in this file.
- UTF-16 validation manually scans two-byte units and must stay consistent with long filename extraction/creation logic.
