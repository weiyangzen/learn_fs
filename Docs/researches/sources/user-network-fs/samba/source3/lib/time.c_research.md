## sources/user-network-fs/samba/source3/lib/time.c

Purpose: Samba source3 time conversion and formatting utilities. It bridges Unix `time_t`/`timespec`, DOS date formats, NT time values, server timezone offset, and process uptime/start time.

Important APIs include `convert_time_t_to_uint32_t`, `convert_uint32_t_to_time_t`, `nt_time_is_zero`, `generalized_to_unix_time`, `get_server_zone_offset`, `set_server_zone_offset`, `srv_put_dos_date`, `srv_put_dos_date2_ts`, `srv_put_dos_date3`, `round_timespec`, `put_long_date_timespec`, `put_long_date_full_timespec`, `pull_long_date_full_timespec`, `put_long_date`, `dos_filetime_timespec`, `make_unix_date*`, `srv_make_unix_date*`, `interpret_long_date`, `TimeInit`, `get_process_uptime`, `get_startup_time`, `nt_time_to_unix_abs`, `unix_to_nt_time_abs`, `time_to_asc`, `display_time`, and `nt_time_is_set`.

Control flow: server date helpers use a process-global `server_zone_offset` initialized by `TimeInit` or `set_server_zone_offset`. Long-date writers round according to requested timestamp resolution before converting to NT time. DOS-date readers delegate to pull helpers with explicit or server zone offset. Absolute NT conversions handle zero, -1, infinity, and 64-bit time bounds specially. Uptime subtracts a saved `start_time_hires` from current time.

State and persistence: static `server_zone_offset` and `start_time_hires` are process-global memory state. No durable state. Dependencies are Samba byte-order macros, DOS/NT time conversion helpers, timeval/timespec utilities, and debug logging.

Risks: `generalized_to_unix_time` ignores timezone suffixes despite parsing generalized time, which can surprise LDAP/ASN.1 consumers. `display_time` uses float arithmetic for 64-bit NT durations and allocates on `talloc_tos`. `TimeInit` only captures startup time once, before daemon fork by design. Tests should cover special time sentinels, 32/64-bit `time_t`, timezone offset initialization, rounding modes, DOS date variants, and generalized-time timezone cases.
