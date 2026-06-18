# File Research: sources/local-fs/xfsdump/common/dlog.h

Purpose: public interface for interactive operator dialogs.

Key declarations:
- Initialization/state:
  - `dlog_init`
  - `dlog_allowed`
  - `dlog_desist`
  - `dlog_fd`
  - `dlog_sighandler`
- Dialog bracketing:
  - `dlog_begin`
  - `dlog_end`
- Multiple-choice prompts:
  - `dlog_multi_query`
  - `dlog_multi_ack`
- String prompts:
  - callback typedefs `dlog_pcbp_t` and `dlog_ucbp_t`
  - `dlog_string_query`
  - `dlog_string_ack`

Important details:
- Exception indices set to `IXMAX` are ignored by the query functions.
- Query functions return either a selected choice index or the caller-provided exception index for timeout/signals.
- The string-query API separates caller rendering from dlog output via callback typedefs.

Interactions:
- Used by content/media-change prompts and other operator intervention flows.
- Relies on common `bool_t`, `ix_t`, and `time32_t` definitions being available to includers.

Risks/notes:
- Callers must bracket multi-step dialogs with `dlog_begin`/`dlog_end` to keep mlog output coherent.
