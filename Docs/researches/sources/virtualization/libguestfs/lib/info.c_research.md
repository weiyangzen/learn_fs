# File Research: sources/virtualization/libguestfs/lib/info.c

Purpose: Implements disk metadata APIs by running `qemu-img info --output json` and parsing its JSON output.

Key behavior:
- `guestfs_impl_disk_format` returns the JSON `format` field.
- `guestfs_impl_disk_virtual_size` returns `virtual-size`.
- `guestfs_impl_disk_has_backing_file` detects presence of `backing-filename`.
- `get_json_output` constructs the qemu-img command, conditionally adds `-U`, forces JSON output, prefixes relative filenames with `./`, captures stdout as one buffer, and checks exit status.
- `parse_json` uses json-c strict UTF-8 validation and reports parse errors through the handle.
- `qemu_img_supports_U_option` probes `qemu-img --help` once and memoizes the result in `g->qemu_img_supports_U_option`.
- Child rlimits bound address space to 1 GiB and CPU to 10 seconds when supported.

Dependencies and state:
- Depends on json-c, command execution helpers, wait status handling, external `qemu-img`, and `guestfs_int_external_command_failed`.
- Mutates only `g->qemu_img_supports_U_option`.

Risks:
- Relies on `qemu-img --help | grep` output for `-U` feature detection.
- JSON schema assumptions are narrow; missing expected keys produce errors.
