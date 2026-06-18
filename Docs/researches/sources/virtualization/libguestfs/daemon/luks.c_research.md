# File Research: sources/virtualization/libguestfs/daemon/luks.c

Small cryptsetup/LUKS helper.

Important behavior:
- Optgroup availability is based on cryptsetup support.
- `do_luks_uuid(device)` runs the LUKS UUID query through cryptsetup and trims command output.
- Errors are reported with command stderr.

Filesystem relevance: exposes encrypted block-device metadata used before mounting contained filesystems.
