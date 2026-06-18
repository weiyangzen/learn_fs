# sources/user-network-fs/libfuse/lib/compat.c

`compat.c` provides ABI compatibility entry points for platforms or builds without versioned symbol support, plus forwarding wrappers for historically versioned libfuse 3.0 symbols.

It forward-declares libfuse public structs and wrappers for `fuse_parse_cmdline`, `fuse_session_custom_io`, `fuse_main_real`, and `fuse_session_new`. Conditional wrappers call `fuse_parse_cmdline_30` and `fuse_session_custom_io_30` only when `LIBFUSE_BUILT_WITH_VERSIONED_SYMBOLS` is not defined. `fuse_main_real` and `fuse_session_new` always forward to `_30` implementations.

Control flow is simple delegation. A preprocessor `#undef fuse_parse_cmdline` avoids public-header macro redirection while defining the unversioned ABI symbol. The file owns no state; the persistent contract is exported symbol compatibility for downstream binaries.

Risks include signature drift, missing unversioned symbols, macro redirection affecting definitions, and forwarding to implementations that no longer preserve old ABI expectations. Test signals include exported-symbol inspection with and without versioned-symbol builds, old consumer compile/link tests, runtime calls through unversioned names, macro conflict checks, and ABI comparison tooling.
