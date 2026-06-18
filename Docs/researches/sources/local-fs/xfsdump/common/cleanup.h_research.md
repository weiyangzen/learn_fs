# File Research: sources/local-fs/xfsdump/common/cleanup.h

Purpose: public cleanup-callback API.

Key declarations:
- Opaque `cleanup_t`.
- `cleanup_init`.
- `cleanup_register(funcp, arg1, arg2)`.
- `cleanup_register_early(funcp, arg1, arg2)`.
- `cleanup_cancel(cleanupp)`.
- `cleanup()` and `cleanup_early()`.

Interactions:
- Used by modules that need deterministic shutdown actions without tying cleanup logic to main control flow.
- Callback signature supports two opaque arguments.

Risks/notes:
- API does not expose ownership beyond the returned handle; callers must cancel only live registrations.
