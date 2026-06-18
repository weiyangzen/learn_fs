# File Research: sources/virtualization/spdk/lib/log/log_flags.c

Implements SPDK's dynamic debug-log flag registry and command-line usage formatting.

Key entry points:
- `spdk_log_register_flag()` registers a named `spdk_log_flag` in case-insensitive sorted order.
- `spdk_log_get_flag()` returns whether a named flag is enabled.
- `spdk_log_set_flag()` and `spdk_log_clear_flag()` enable or disable flags by exact/wildcard pattern, with special support for `"all"`.
- `spdk_log_get_first_flag()` and `spdk_log_get_next_flag()` iterate registered flags.
- `spdk_log_usage()` prints the `--logflag` help text with line wrapping.

Core mechanics:
- Flag lookup is case-insensitive through `strcasecmp()`.
- Pattern setting/clearing uses `fnmatch(..., FNM_CASEFOLD)` so callers can enable groups of flags by wildcard.
- Duplicate registration or missing registration parameters logs an error and asserts.
- Usage output wraps around a 100-character line limit using a fixed continuation prefix.

Important invariants:
- Registered flags must remain valid for the lifetime of the registry; this file stores caller-owned `struct spdk_log_flag` pointers.
- The list is kept sorted by flag name to produce stable usage output.
- `"all"` is handled before wildcard matching and applies to every registered flag.

Filesystem/block relevance:
- Component-specific debug flags are heavily used by SPDK storage modules. This registry controls targeted debug output without globally raising log verbosity.

Notable risks:
- The global flag list is not locked, so registration and flag updates are expected during controlled initialization or from serialized control paths.
- `spdk_log_usage()` assumes the flag list is stable while it formats help output.
