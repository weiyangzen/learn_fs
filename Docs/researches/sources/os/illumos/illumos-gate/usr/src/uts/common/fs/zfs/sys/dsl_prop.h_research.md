# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_prop.h

Read status: complete, 124 lines.

Purpose: DSL property lookup, inheritance, setting, and callback interface.

Key structures and APIs:
- `dsl_prop_changed_cb_t` callbacks receive a new integer value and must not call into DMU or DSL.
- `dsl_prop_record_t` tracks a property name and callback list under a dsl_dir.
- `dsl_prop_cb_record_t` links callback registrations to property records and datasets.
- Argument structs support property get/set synctasks.
- APIs initialize/finalize dsl_dir property state, register/unregister/notify callbacks, get properties by dataset name/dataset/dir, get all/received props, set properties through check/sync paths, set integer/string props, inherit props, predict inherited values, track received-properties availability, and add typed property values to nvlists.

Dependencies: DMU, DSL pool, ZFS context, DSL synctask.

Research notes:
- This header owns the inheritance/callback control plane for dataset properties.
- Callback restriction is important for avoiding recursive DSL/DMU entry.
