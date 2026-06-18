# sources/test-tools/strace/bundled/linux/include/uapi/linux/dm-ioctl.h

Purpose: defines the traditional device-mapper ioctl ABI for `/dev/mapper/control` and related block-device operations.

Important APIs/types/functions: constants define mapper/control names, type/name/UUID lengths, ioctl base `DM_IOCTL`, interface version `4.50.0`, command enum IDs, ioctl macros such as `DM_VERSION`, `DM_DEV_CREATE`, `DM_DEV_SUSPEND`, `DM_TABLE_LOAD`, `DM_TABLE_STATUS`, `DM_TARGET_MSG`, and `DM_MPATH_PROBE_PATHS`. Main payloads are `struct dm_ioctl`, `dm_target_spec`, `dm_target_deps`, `dm_name_list`, `dm_target_versions`, and `dm_target_msg`. Flag bits cover readonly, suspend, persistent dev, status-table query, active/inactive table presence, buffer full, noflush, query inactive, uevent/cookie behavior, UUID rename, secure data wiping, deferred remove, internal suspend, and IMA measurement.

Control flow: userspace sends one memory block beginning with `struct dm_ioctl`; `data_start`, `data_size`, and command-specific variable records describe appended table specs, dependency arrays, device lists, versions, messages, or geometry strings. Device-mapper has active and inactive table slots, and suspend/resume/table-load commands move state between them.

State and persistence behavior: device-mapper state is kernel runtime block-device state: mapped devices, active/inactive target tables, open counts, event numbers, udev cookies, deferred removal, and optional geometry. Some target tables may reference persistent backing devices, but this header itself describes ioctl exchange state.

Dependencies: includes `<linux/types.h>` and uses Linux ioctl encoding macros expected from userspace build context.

Integration points: strace decodes device-mapper ioctls, version triplets, flags, names/UUIDs, table specs, and variable-length lists. Device-mapper tools use this ABI for all legacy control operations.

Risks: variable-length records rely on offsets with two different `next` interpretations for load versus status paths. `struct dm_ioctl.data[7]` is padding/data start space, not a normal C string. Sensitive-data flag has security implications for buffers. Version extra string indicates this bundled header is recent and decoder tables should not assume older command ceilings.

Test signals: ioctl decode tests should cover version query, device create/remove/rename, table load/status with multiple target specs, list devices with UUID flags, buffer-full return, uevent cookie/event number fields, and secure-data/noflush/deferred-remove flags.
