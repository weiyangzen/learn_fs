# File Research: sources/virtualization/libblockdev/src/utils/extra_arg.h

This public header defines the `BDExtraArg` boxed type.

Contents:
- `BD_UTIL_TYPE_EXTRA_ARG` macro.
- `bd_extra_arg_get_type()` declaration.
- `BDExtraArg` struct with owned `gchar *opt` and `gchar *val`.
- Copy, free, list-free, and constructor declarations.

Research relevance:
- `BDExtraArg` is the common typed transport for optional command-line switches across many plugins and language bindings.
