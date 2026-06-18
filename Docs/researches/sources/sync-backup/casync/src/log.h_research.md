# sources/sync-backup/casync/src/log.h

Purpose: public declaration layer for casync logging and assertion helpers.

Important APIs/types/functions: declares the three errno-aware log functions, macro aliases `log_info`, `log_error`, `log_debug`, `log_oom`, `assert_se`, `assert_not_reached`, `set_log_level`, and `set_log_level_from_string`. `_printf_` annotations let the compiler check format strings.

Control flow/state: no runtime state lives here, but `assert_se` evaluates an expression and logs a fatal-style error before calling `abort` on false. `assert_not_reached` always logs and aborts.

Dependencies/integration: includes `gcc-macro.h` for compiler annotations and errno types for `-ENOMEM` reporting. Many source and test files use `assert_se` as a hard test oracle.

Risks/test signals: `assert_se` remains active in release-style builds unlike standard `assert`, so callers must avoid expressions with unacceptable side effects in production paths. The header is heavily exercised by every C test binary.

Source research group: `subset-b-009122`.
