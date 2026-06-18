# File Research: sources/local-fs/dlm/dlm_sand/log.h

This header declares `dlm_sand` logging macros and the printf-checked `log_level()` function.

Key contents:
- `log_level(char *ls_name, int level, const char *fmt, ...)` with GCC printf format checking.
- Convenience macros:
  - `log_debug`
  - `log_space`
  - `log_warn`
  - `log_warns`
  - `log_error`
  - `log_erros`
  - `log_info`
  - `log_print`

Intended severity destinations:
- Errors go to syslog and the `dlm_sand` logfile.
- Warnings/info go to the logfile.
- Debug goes to the in-core dump buffer unless debug output is enabled.

Notable detail:
- `log_erros(space, ...)` expands to `log_level(ls->name, ...)` but the macro parameter is named `space`; this appears inconsistent and would only compile correctly where an `ls` identifier is in scope. It may be unused or a typo.
