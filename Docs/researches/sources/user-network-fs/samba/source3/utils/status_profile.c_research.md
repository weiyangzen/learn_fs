# sources/user-network-fs/samba/source3/utils/status_profile.c

## Purpose

`sources/user-network-fs/samba/source3/utils/status_profile.c` implements `smbstatus` profile dumping and profile rate display when Samba is built with profiling support. It prints raw profile counters, JSON profile counters, per-service profile sections, and a continuous one-second rate view. The source was read as a complete 511-line file.

## Important APIs, Types, and Functions

Public functions are `status_profile_dump` and `status_profile_rates`. Helpers include `profile_separator`, `print_buckets`, `status_profile_dump_persvc_stats`, `status_profile_dump_persvc_cb`, `status_profile_dump_persvc`, rate printers for count/basic/bytes/iobytes stats, and `print_count_samples`. The implementation relies heavily on `SMBPROFILE_STATS_ALL_SECTIONS` macro expansion.

## Control Flow

`status_profile_dump` initializes profile shared memory with `profile_setup`, collects a `profile_stats` snapshot, and expands profile macros to print each counter or add JSON fields. In JSON mode it also collects per-service stats with `smbprofile_persvc_collect`. `status_profile_rates` initializes profiling, collects alternating samples, computes deltas once per second, prints active rates, swaps sample buffers, and sleeps until the next sample.

## State and Persistence Behavior

It reads profiling shared memory but does not persist data. Rate mode keeps static two-element `sample_data` and `sample_time` buffers for delta calculations and runs indefinitely until interrupted.

## Dependencies and Integration Points

It depends on `smbprofile.h`, `status_profile.h`, `conn_tdb`, generated open-files types, and `status_json.h`. `status.c` dispatches to it for `-P` and `-R`; `wscript_build` selects this file only when `WITH_PROFILE` is enabled.

## Risks and Edge Cases

The macro-based counter expansion must stay synchronized with `smbprofile` structures. Rate conversion divides by elapsed seconds after converting microseconds, so unusually short or skewed intervals can produce zero or misleading rates; the code guards only zero microsecond deltas. Rate mode is intentionally infinite. JSON profile output depends on the JSON section hierarchy already being valid.

## Test Signals

Tests should cover text and JSON dumps, no-profile-memory failure, per-service profile collection, rate output with synthetic sample deltas, verbose delay logging, and build selection with `WITH_PROFILE` on/off.
