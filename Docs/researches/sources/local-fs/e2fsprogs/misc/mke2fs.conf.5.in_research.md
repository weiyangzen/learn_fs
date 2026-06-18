# File Research: sources/local-fs/e2fsprogs/misc/mke2fs.conf.5.in

`mke2fs.conf.5.in` is the manual page template for the `mke2fs.conf` configuration file.

Documented format:
- INI-style syntax with top-level stanzas in brackets.
- Relations assign tags to scalar values or nested subsections.
- Duplicate tags are permitted.
- Comments begin with `;` or `#`.
- Values with spaces require double quotes.
- Standard backslash escapes are documented.
- Boolean parsing is liberal, accepting common true/false spellings.

Documented stanzas:
- `[options]`: controls formatter behavior.
- `[defaults]`: global defaults.
- `[fs_types]`: defaults for filesystem and usage profiles selected by `-t`, `-T`, device settings, or size.
- `[devices]`: per-device defaults.

Important documented options:
- `[options]`: `proceed_delay`, `sync_kludge`.
- `[defaults]`: `creator_os`, `fs_type`, `undo_dir`, plus filesystem tags also valid in fs type subsections.
- `[fs_types]`: feature sets, periodic fsck, error behavior, force_undo, auto 64-bit support, mount options, blocksize, lazy init, journal location, sparse_super2 backups, packed metadata, inode ratio/size, reserved ratio, hash algorithm, flex_bg size, default extended options, discard, RAID stride/stripe policy, cluster size, hugefile options, Y2038 warning, casefold encoding settings.
- `[devices]`: `fs_type`, `usage_types`.

Hugefile documentation:
- Explains `make_hugefiles`, target directory, uid/gid/umask, count, slack, size, alignment, disk-relative alignment, basename, digits, and zeroing behavior.
- Notes that hugefiles are intended to place extent tree blocks early and data contiguously.

Research notes:
- This man page describes the configuration model consumed directly by `mke2fs.c` and `mk_hugefiles.c`.
- It documents the fs type precedence rule: later entries in the constructed fs type list override earlier scalar settings, while `features` entries are cumulative.
- It includes newer feature defaults such as casefold encoding and orphan file sizing.
