# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/modeedit.c

## Purpose
Displays and edits SCSI mode pages and block descriptors using a mode-page format database.

## Main Elements
- Maintains editable fields in `editlist` and page names in `namelist`.
- `load_format()`: parses `/usr/share/misc/scsi_modes` or `$SCSI_MODES`, collecting page names and selected page format.
- `editlist_populate()` / `editlist_populate_desc()`: MODE SENSE current/changeable data and decode into edit entries.
- `editentry_set()` validates integer/string changes, clips out-of-range integers, and tracks changed state.
- `modepage_write()` / `modepage_read()`: serialize editable fields and parse edited values.
- `modepage_edit()`: reads changes from stdin when noninteractive, otherwise invokes `$EDITOR` or `vi` on a temp file.
- `editlist_save()` / `editlist_save_desc()`: MODE SENSE current data, encode edited values, clear reserved fields, then MODE SELECT.
- `modepage_dump()` / `modepage_dump_desc()`: raw hex fallback.
- `mode_edit()`: top-level display/edit path.
- `mode_list()`: queries all pages and prints page/subpage IDs with names from the database.

## Dependencies And Integration
Uses CAM MODE SENSE/SELECT wrappers from other `camcontrol` code and SCSI buffer encode/decode visitor helpers.

## Risk Notes
Edit mode can change device configuration, including saved values. The code restricts editing to current or saved page controls and falls back to binary display when database formatting is unavailable in non-edit mode.
