# File Research: sources/virtualization/guestfs-tools/edit/edit.c

`virt-edit` command implementation. It creates a writable libguestfs handle, parses common disk/domain/mount/key options, launches the appliance, mounts the guest either via inspection or explicit `-m`, then edits one or more guest files.

Key behavior:
- Supports `-a`, `-d`, `--format`, `--blocksize`, `--key`, `--keys-from-stdin`, `--connect`, `-m`, `-b`, and `-e/--expr`.
- Defaults to inspector-based mounting; `-m` disables inspection.
- Preserves compatibility with old syntax by treating pre-filename arguments as disks or domains when no explicit drive options were given.
- For Windows guests, translates guest paths through `windows_path`.
- Actual edits are delegated to shared helpers:
  - `edit_file_perl` for noninteractive Perl expression editing.
  - `edit_file_editor` for `$EDITOR`-based editing.
- Supports backup extension creation through `backup_extension`.
- Shuts down libguestfs cleanly after edits.

Important dependencies: `guestfs.h`, common `options.h`, `display-options.h`, `windows.h`, and `file-edit.h`.

Research relevance: this file is a user-facing guest filesystem mutation tool. It demonstrates libguestfs write-mode setup, guest root discovery, Windows path normalization, and safe delegation of in-guest file replacement logic.
