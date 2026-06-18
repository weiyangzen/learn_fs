# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_susp.h

This header defines System Use Sharing Protocol support for HSFS, including SUSP field parsing helpers and extension dispatch structures.

Return codes:
- SUSP parser returns negative sentinel codes for null pointer, end of parsing, end of SUA, continuation request, allocation failure, invalid data, and relocated-directory handling.

Extension implementation bits:
- Macros set, clear, and test extension bits in `hsfs_ext_impl`.
- Defined bits include SUSP present and prohibited file/dir type present.
- SUSP-specific macros mark and test whether SUSP is implemented.

SUSP signatures:
- Defines signatures `SP`, `CE`, `PD`, `ER`, and `ST`.
- SUSP version is 1.

System Use Field access:
- Generic SUF macros parse signature length, field length, and version.
- Extension Reference macros parse id/description/source lengths, extension version, and locate extension id/description/source strings.
- Continuation Area macros parse block location, offset, and length.
- Sharing Protocol macros parse check bytes and SUA offset.
- Check bytes are `0xBE` and `0xEF`.

Dispatch structures:
- `ext_signature_t` maps a two-character extension signature to a handler function.
- `extension_name_t` maps extension names and versions to signature tables.
- `cont_info_t` carries continuation area location/offset/length.
- `sig_args_t` bundles arguments passed to signature handlers, including dir entry pointer, name buffer/length, flags, name flags, current SUF pointer, parsed hs_direntry, filesystem pointer, and continuation info.

Kernel declarations:
- Declares handlers for SUSP SP, ER, CE, PD, and ST fields.
- Declares RRIP and SUSP signature tables, extension-name table, SUSP SP pointer, and `parse_sua()`.

Dependencies and relationships:
- Provides the extension dispatch substrate used by RRIP support in `hsfs_rrip.h`.
- Uses ISO/HSFS directory record system-use areas to discover and process filesystem extensions.
