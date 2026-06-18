# sources/security-integrity/selinux/libselinux/src/callbacks.c

Purpose: `callbacks.c` stores global libselinux callback hooks for logging, supplemental audit, context validation, setenforce notification, and policyload notification, with default implementations.

Important APIs/types/functions: exported APIs are `selinux_set_callback()` and `selinux_get_callback()`. Global callback pointers are `selinux_log_direct`, `selinux_audit`, `selinux_validate`, `selinux_netlink_setenforce`, and `selinux_netlink_policyload`. `log_mutex` protects log output.

Control flow: defaults log to `stderr`, no-op audit/netlink callbacks, and validate contexts through `security_check_context()` unless building host tools. `selinux_set_callback()` switches by public callback type and replaces the matching pointer. `selinux_get_callback()` returns the current pointer or sets `EINVAL` for unknown types.

State and persistence: callback state is process-global and persists until replaced or process exit. No filesystem state is modified.

Dependencies and integration: used by label validation, AVC event forwarding, and logging across libselinux. The header macro `selinux_log()` wraps these pointers with mutex and errno preservation.

Risks and test signals: global callback mutation is not guarded by its own setter lock. Callback implementations can change library behavior broadly. Tests should cover default validation with and without `BUILD_HOST`, unknown callback type errno, logging errno preservation, and callback replacement.
