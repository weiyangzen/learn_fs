# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_set.h

This header declares channel-program property-setting synctask support.

Core definitions:
- `zcp_set_prop_arg_t` stores Lua state, dataset name, property name, and property value string for a set-property synctask.

Public API surface:
- `zcp_set_prop_check()` validates a property set in synctask check context.
- `zcp_set_prop_sync()` applies the property set in sync context.

Risk-sensitive invariants:
- Check and sync phases must share stable argument state and obey DMU transaction context.
- Dataset/property/value strings are passed by pointer and must remain valid for the synctask lifetime.
