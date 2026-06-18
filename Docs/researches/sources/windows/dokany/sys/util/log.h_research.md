# File Research: sources/windows/dokany/sys/util/log.h

Dokan logging API, global cache types, debug macros, IRP logging macros, Event Log helpers, and compact backtrace declarations.

Key responsibilities:
- Defines debug bit flags for normal, lock, and oplock logging.
- Declares global debug state and the `DOKAN_LOG_CACHE`/`DOKAN_LOG_ENTRY` structures.
- Declares cached-log functions: push, clean, enable-check, and active-VCB count increment.
- Defines `DDbgPrint`, timestamped cache push, cached log, no-cache log, and request-aware logging macros.
- Provides IRP-specific logging helpers for begin/end dispatch, IOCTL names, major/minor function names, device-extension type, completion, and status.
- Declares stringification functions implemented in `log.c`.
- Defines `DOKAN_LOGGER`, its initializer macro, Event Log functions, and compact `DokanBackTrace`.

Important behavior:
- `DOKAN_CACHED_LOG` debug-prints when `g_Debug` is enabled and pushes into the cache only at `PASSIVE_LEVEL` when caching is enabled.
- `DOKAN_LOG_INTERNAL` respects `RequestContext->DoNotLogActivity`.
- `DOKAN_LOG_END_MJ` may complete the IRP unless `DoNotComplete` is set or the status is pending.
- `DOKAN_LOG_VCB` synthesizes a temporary `REQUEST_CONTEXT` so VCB-level logs can reuse request-aware caching.
- `DOKAN_DENIED_LOG_EVENT` suppresses noisy event-pull FSCTL logging.

Dependencies:
- Includes `<ntifs.h>` and relies on Dokan types included before/around it in core compilation units.
- Macros call functions from `log.c` and core Dokan completion/event code.

Notable risks:
- Many logging helpers are macros with side effects; call sites must pass valid request contexts and avoid arguments with unwanted repeated evaluation.
- `DOKAN_LOG_END_MJ` is not only logging; it can complete an IRP, so it is part of dispatch control flow.
- Cached logging format paths depend on variadic macro correctness and function-scope `__FUNCTION__`.
