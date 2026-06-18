# sources/test-tools/strace/src/statx.c

Purpose: decodes `statx` inputs and the extended output `struct_statx`.

Important APIs/types/functions: `print_statx_timestamp`, `SYS_FUNC(statx)`, `struct_statx`, `struct_statx_timestamp`, `statx_masks`, `statx_attrs`, `at_statx_sync_types`, and `print_symbolic_mode_t`.

Control flow: entry prints dirfd, pathname, flags split into statx sync type plus generic `AT_*` flags, and requested mask. Exit fetches statx buffer, prints returned mask, block size in full mode, attributes, and then conditionally prints fields based on returned mask and attribute bits. Abbreviated mode prints core fields and `...`; full mode includes timestamps with human-readable comments, device ids, mount id, DIO alignment, subvolume, atomic write fields, and DIO read alignment.

State and persistence behavior: stateless local fetch of output buffer on exit.

Dependencies and integration points: uses local `statx.h` layout rather than relying solely on system headers, plus common path/fd/mode/time printers.

Risks: statx continues to grow; local struct layout and conditional field masks must track kernel UAPI. Attribute-gated atomic write fields depend on `STATX_ATTR_WRITE_ATOMIC`, while other fields depend on `stx_mask`.

Test signals: all major mask bits, abbrev/full modes, timestamp comments, atomic write attributes, DIO alignment/read alignment, sync-type flags mixed with generic flags, invalid output pointer, and unknown masks/attributes.
