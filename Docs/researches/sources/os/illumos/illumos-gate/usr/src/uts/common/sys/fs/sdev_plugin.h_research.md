# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/sdev_plugin.h

This header defines the kernel plugin interface for sdev dynamic `/dev` nodes.

Opaque handles:
- `sdev_plugin_hdl_t` identifies a registered plugin.
- `sdev_ctx_t` identifies an sdev callback context.

Validation results:
- Invalid, skip, valid, and stale outcomes are represented by `sdev_plugin_validate_t`.

Plugin flags:
- `SDEV_PLUGIN_NO_NCACHE` disables negative cache use.
- `SDEV_PLUGIN_SUBDIR` marks plugin handling for subdirectories.
- Valid flags are masked by `SDEV_PLUGIN_FLAGS_MASK`.

Plugin operations:
- `sp_valid_f` validates a context.
- `sp_filldir_f` fills a directory.
- `sp_inactive_f` handles inactive nodes.
- `sdev_plugin_ops_t` stores version, flags, and callbacks.
- Plugin interface version is 1.

Registration and context helpers:
- Register/unregister plugin by name.
- Query context flags, name, path, minor number, vnode type.
- Create directories and special nodes through plugin callbacks.

Dependencies and relationships:
- The implementation side is declared in `sdev_impl.h`.
- Provides a narrow extension interface for modules that populate or validate dynamic `/dev` subtrees.
