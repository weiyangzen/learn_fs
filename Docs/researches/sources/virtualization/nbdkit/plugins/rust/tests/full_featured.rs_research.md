# File Research: sources/virtualization/nbdkit/plugins/rust/tests/full_featured.rs

Comprehensive tests for a Rust plugin registering all supported optional callbacks. Initialization asserts static metadata fields (`config_help`, description, longname, magic config key, name, version) and creates plugin tables with every optional callback selected in `plugin!`.

The test modules cover block-size output pointers, boolean capability callbacks, cache/FUA enum conversions, cache/flush/write/trim/zero callbacks, config/config_complete/get_ready/after_fork/preconnect/thread_model error handling, static lifecycle callbacks, metadata strings, and pwrite flag conversion. Extent tests verify both plugin-level errors and errors returned by `ExtentHandle::add`, plus REQ_ONE flag translation.

The file's main purpose is ABI-contract coverage: it ensures Rust trait returns are converted into nbdkit C return codes, errno, and messages consistently, and that callback pointers are present only when registered.
