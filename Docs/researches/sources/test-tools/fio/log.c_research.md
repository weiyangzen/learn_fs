# sources/test-tools/fio/log.c

Purpose: common text logging for fio info, error, debug-prefix, buffer-backed, backend, and syslog outputs.

Important APIs/functions: `log_info_buf`, `log_valist`, optional `log_prevalist`, `log_info`, `__log_buf`, `log_info_flush`, `log_err`, and `log_get_level`.

Control flow: info logging first tries backend server text output, then syslog, then `f_out`. Error logging formats into a heap buffer, sends to backend if possible, otherwise syslog or `stderr` plus `f_err`. `__log_buf` formats into temporary storage and appends to a `buf_output`. Debug prefixing adds level name and thread id when debug filtering allows it.

State/persistence: uses global output streams `f_out`, `f_err`, and global flags such as `is_backend` and `log_syslog`. It allocates temporary formatted strings with `vasprintf/asprintf`.

Dependencies/integration: includes `fio.h`, server output paths, syslog, and `oslib/asprintf`. `log_buf` in the header routes callers here.

Risks/test signals: `fwrite` return values are item counts, not byte counts, so callers should not overinterpret returned lengths. Error logging writes to both stderr and `f_err` when distinct. Tests should cover backend fallback, syslog mode, null info buffer, and buffer appends.
