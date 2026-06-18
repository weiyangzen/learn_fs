# sources/test-tools/fio/profiles/act.c

Purpose: implements the ACT "Aerospike-like" fio profile with generated workloads and latency pass/fail criteria.

Important APIs/functions: static profile registration via `fio_init act_register()` and `fio_exit act_unregister()`. Profile callbacks include `act_prep_cmdline()`, `act_td_init()`, `act_td_exit()`, and `act_io_u_lat()`. Helpers build option strings (`act_add_opt()`, `act_add_rw()`, `act_add_dev_prep()`, `act_add_dev()`), aggregate latency slices, and print final stats.

Control flow: profile options collect device names, load, duration, queue/thread parameters, read block count, write size, and prep mode. `act_prep_cmdline()` splits comma-separated devices and generates fio jobs. Normal mode creates runtime/time-based read and write jobs per device with derived rates; prep mode writes zeroes and random salt. During IO, `act_io_u_lat()` buckets latency by criteria per one-hour sample and returns failure when thresholds are exceeded. Thread init allocates per-thread slices and increments a shared pending count; thread exit merges slices under a fio semaphore and prints aggregate pass/fail when the last thread exits.

State and persistence: global `act_opts` grows with dynamically allocated option strings; global `act_run_data` holds the semaphore, pending thread count, and aggregate slices. Per-thread state lives in `td->prof_data`.

Dependencies and integration: profile framework, parser option types, fio semaphores, timing (`fio_gettime`, `time_since_now`), logging, and thread lifecycle hooks.

Risks: `act_options.device_names` is destructively modified by `strsep()`, so reload/reuse semantics are fragile. Option cleanup loop in `act_unregister()` increments before freeing and may skip or overrun depending on `org_idx`/`opt_idx`. Default `test_duration` is parsed as a time value but later formatted as seconds with `%llus`; unit expectations need confirmation. This profile drives real destructive writes to named devices.

Test signals: profile option parsing, generated command-line contents for prep and normal mode, multiple devices, latency bucket aggregation, failure thresholds, and unregister memory cleanup.
