# sources/test-tools/fio/log.h

Purpose: declares fio logging APIs and severity constants.

Important APIs/types: global `FILE *f_out`/`f_err`, printf-checked `log_err` and `log_info`, `__log_buf`, `log_valist`, `log_prevalist`, `log_info_buf`, `log_info_flush`, `log_get_level`, and macro `log_buf`.

Control flow/state: `log_buf` writes into a provided `buf_output` or falls back to `log_info` when the buffer is null. Severity enum values map debug/info/error levels.

Dependencies/integration: includes `output_buffer.h`, stdio, stdarg, and unistd. Widely used across fio for status and diagnostics.

Risks/test signals: macro evaluates the buffer argument more than once only as written in the conditional expression; callers should avoid side-effect arguments. Compile tests should preserve printf attribute checking.
