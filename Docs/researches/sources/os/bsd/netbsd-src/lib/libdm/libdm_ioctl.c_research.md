# File Research: sources/os/bsd/netbsd-src/lib/libdm/libdm_ioctl.c

This file implements the NetBSD libdm userspace API. It wraps device-mapper operations in proplib dictionaries/arrays and exchanges them with the kernel device-mapper driver through `NETBSD_DM_IOCTL` on `/dev/mapper/control`.

Key structures:
- `struct libdm_task` owns a top-level `prop_dictionary_t`.
- `struct libdm_cmd` owns a `prop_array_t` command-data array.
- `struct libdm_table`, `struct libdm_target`, and `struct libdm_dev` wrap proplib dictionaries.
- `struct libdm_iter` wraps a proplib object iterator.
- `cmd_ver[]` maps command names like `version`, `targets`, `create`, `info`, `remove`, `reload`, `status`, and `table` to version `{4,0,0}`.

Key control flow:
- `libdm_task_create()` allocates a dictionary, sets `DM_IOCTL_COMMAND`, and adds a version array when the command appears in `cmd_ver`.
- `libdm_task_run()` opens `DM_DEVICE_PATH`, sends the dictionary via `prop_dictionary_sendrecv_ioctl()` or rump plistref ioctl path, closes the fd, releases the old dictionary, and replaces it with the response dictionary.
- Setters store strings, integers, flags, tables, and command arrays under kernel protocol keys from `<dev/dm/netbsd-dm.h>`.
- Getters read values from response dictionaries and arrays.
- Iterators expose command arrays as target/table/dev/dependency sequences.

API coverage:
- Task name/uuid/minor/flags/open/event/target count accessors.
- Specific flag mutators for suspend, status-table, and exists flags.
- Command creation, destruction, table attachment, iteration.
- Table creation/destruction and field accessors for start, length, target type, params, and status.
- Target and device wrapper destruction/accessors.
- Rename support through `libdm_dev_set_newname()` storing a string at array index 0.

Risks and notes:
- Several allocation paths do not check every intermediate proplib allocation result.
- Some getters do not initialize local variables before `prop_dictionary_get_*` failure paths, so callers must avoid relying on values after malformed responses.
- `libdm_cmd_get_deps()` calls `prop_number_unsigned_value(obj)` before checking whether `obj` is NULL.
- Wrapper objects returned by iterator getters do not consistently retain underlying proplib objects, but destroy routines release them; this requires careful proplib ownership expectations.
- Error return conventions are mixed: some APIs return `ENOENT`, some return booleans from proplib setters, some return `EXIT_SUCCESS`, and ioctl errors are propagated differently under rump/non-rump paths.
