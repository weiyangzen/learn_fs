# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dacf.h

Public Device Autoconfiguration Framework interface. It defines DACF module/opset descriptors, operation IDs, client information handles, client helper accessors, and success/failure return codes.

Key elements:
- Defines DACF interface revision `DACF_MODREV_1`.
- Opaque handles `dacf_arghdl_t` and `dacf_infohdl_t` represent operation arguments and device/minor information.
- Operation IDs include post-attach and pre-detach hooks, plus error/end sentinels.
- `dacf_op_t` maps an operation ID to a callback function.
- `dacf_opset_t` groups a named, null-terminated set of operations.
- `struct dacfsw` is the module-visible DACF switch with revision and opsets; `kmod_dacfsw` is the kernel-provided module symbol.
- Client helper functions retrieve minor name/number, dev_t, driver name, devinfo node, named arguments, stored per-info data, and vnode creation.
- Defines `DACF_SUCCESS` and `DACF_FAILURE`.

Dependencies:
- Uses DDI device/minor types through included `sys/types.h` and externally visible `dev_info_t`/`vnode` declarations.
- Implemented by DACF core and consumed by DACF modules that register post-attach/pre-detach actions.

Research notes:
- Operation arrays and opset arrays are null/sentinel terminated, so module definitions must include `DACF_OPID_END`.
- The framework lets callbacks store/retrieve per-info private state, which is important for pairing post-attach setup with pre-detach teardown.
