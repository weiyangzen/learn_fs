# File Research: sources/os/bsd/netbsd-src/lib/libdm/dm.h

This public header declares NetBSD libdm's opaque handle API for constructing and running device-mapper ioctl tasks.

Key types:
- Opaque pointer typedefs: `libdm_task_t`, `libdm_cmd_t`, `libdm_target_t`, `libdm_table_t`, `libdm_dev_t`, and `libdm_iter_t`.
- `struct cmd_version` maps command strings to version triples.

Key API groups:
- Task lifecycle and execution: `libdm_task_create()`, `libdm_task_destroy()`, `libdm_task_run()`.
- Task metadata: name, uuid, minor, command string, command version, flags, open count, event count, target count.
- Flag helpers for suspend/status/exists/nocount-style protocol bits.
- Command arrays: create/destroy/iterate and attach tables.
- Table dictionaries: start, length, target type, params, status.
- Target dictionaries: name and version.
- Device dictionaries: name, minor, rename new-name.

Integration:
- `DM_DEVICE_PATH` is `/dev/mapper/control`.
- The implementation in `libdm_ioctl.c` translates these APIs to proplib dictionaries and NetBSD DM ioctl keys.

Risks and notes:
- Ownership semantics are not obvious from the header: several getters return pointers into property objects rather than caller-owned strings.
- The header has a comment typo around “dictonaries” but no functional issue.
