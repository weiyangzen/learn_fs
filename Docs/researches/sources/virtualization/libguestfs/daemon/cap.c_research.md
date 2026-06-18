# File Research: sources/virtualization/libguestfs/daemon/cap.c

Implements Linux file capability get/set support when libcap is available.

Key points:
- `optgroup_linuxcaps_available` reports availability under `HAVE_CAP`.
- `do_cap_get_file` calls `cap_get_file` inside the sysroot; `ENODATA` is normalized to an empty string.
- Capability text returned by libcap is duplicated before `cap_free`.
- `do_cap_set_file` parses text via `cap_from_text` and applies it inside the sysroot.
- Without libcap, `OPTGROUP_LINUXCAPS_NOT_AVAILABLE` is used.
