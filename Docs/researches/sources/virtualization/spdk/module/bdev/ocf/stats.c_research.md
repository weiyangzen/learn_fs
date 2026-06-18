# File Research: sources/virtualization/spdk/module/bdev/ocf/stats.c

This file collects and serializes OCF per-core statistics. `vbdev_ocf_stats_get()` looks up an OCF core by name in a cache and calls `ocf_stats_collect_core()` to fill usage, request, block, and error stat groups. `vbdev_ocf_stats_reset()` finds the same core and reinitializes its stats.

`vbdev_ocf_stats_write_json()` writes a nested JSON object with four groups: `usage`, `requests`, `blocks`, and `errors`. The `WJSON_STAT` macro emits each field as an object containing raw count, decimal percentage string, and units.

The units are fixed by stat group: usage and block stats use 4 KiB blocks, request and error stats use requests. The file depends on OCF's stats structures and SPDK JSON writers, with no asynchronous behavior.
