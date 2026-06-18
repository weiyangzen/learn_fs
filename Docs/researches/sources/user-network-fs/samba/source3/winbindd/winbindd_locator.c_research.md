# sources/user-network-fs/samba/source3/winbindd/winbindd_locator.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_locator.c

`winbindd_locator.c` owns the singleton locator child used by winbindd for DC locator work. The file is intentionally small: it keeps a file-static `struct winbindd_child *static_locator_child`, exposes it through `locator_child()`, tests identity with `is_locator_child()`, returns its wbint binding handle through `locator_child_handle()`, and allocates it in `init_locator_child()`.

The control flow is a one-time initialization path. `init_locator_child()` refuses double allocation with `NT_STATUS_INTERNAL_ERROR`, allocates a zeroed child under the supplied talloc context, and delegates setup to `setup_child(NULL, static_locator_child, "log.winbindd", "locator")`. Passing `NULL` as the domain marks this as a special-purpose child rather than a domain child. After setup, callers use `locator_child_handle()` to send internal RPC requests to the locator process.

State is process-local and persistent for the lifetime of the parent process or the memory context that owns the child. There is no on-disk state. Dependencies are `winbindd.h`, talloc, the generic child setup code, and the child binding handle initialized elsewhere. Integration points include winbindd startup, child classification, logging with the `locator` suffix, and any command that routes locator work through the locator child.

The main risks are lifecycle assumptions: `locator_child_handle()` dereferences without a NULL check, so callers must only use it after successful initialization; double initialization is treated as an internal error; and cleanup depends on the owner context. Test signals are startup initialization, duplicate init failure, `is_locator_child()` discrimination from domain/idmap children, and successful wbint binding use through the locator child.
