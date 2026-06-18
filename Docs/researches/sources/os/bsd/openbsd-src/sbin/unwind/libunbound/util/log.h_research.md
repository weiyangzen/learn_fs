# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/log.h

Public API for Unbound logging.

Key contents:
- Defines `enum verbosity_value`:
  - `NO_VERBOSE`
  - `VERB_OPS`
  - `VERB_DETAIL`
  - `VERB_QUERY`
  - `VERB_ALGO`
  - `VERB_CLIENT`
- Declares global `verbosity`.
- Declares logging lifecycle/configuration:
  - `log_init`
  - `log_file`
  - `log_thread_set`
  - `log_thread_get`
  - identity setters/reverters
  - ASCII/ISO timestamp setters
  - `log_get_lock`
- Declares message functions:
  - `verbose`
  - `log_info`
  - `log_err`
  - `log_warn`
  - `log_query`
  - `log_reply`
  - `fatal_exit`
  - `log_vmsg`
- Declares binary diagnostics:
  - `log_hex`
  - `log_buf`
- Defines `log_assert(x)`:
  - active only under `UNBOUND_DEBUG`;
  - uses `assert(x)` for clang analyzer;
  - otherwise calls `fatal_exit` with file, line, function, and expression.
- Windows-only declaration:
  - `wsa_strerror(DWORD err)` under `USE_WINSOCK`.

Research notes:
- Uses `ATTR_FORMAT` on printf-like APIs and `ATTR_NORETURN` on `fatal_exit`, so callers get compiler checking when configured.
- This is a central dependency for locks, network helpers, module utilities, and diagnostics.
