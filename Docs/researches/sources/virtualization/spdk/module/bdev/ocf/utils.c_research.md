# File Research: sources/virtualization/spdk/module/bdev/ocf/utils.c

This file provides string conversion helpers for OCF cache modes and sequential cutoff policies plus the generic asynchronous management-operation runner used by `vbdev_ocf.c`.

Cache mode strings map OCF enum values to `wt`, `wb`, `wa`, `pt`, `wi`, and `wo`. Unknown mode names return `ocf_cache_mode_none`. Sequential cutoff policy strings map to `always`, `full`, and `never`; unknown policies return `ocf_seq_cutoff_policy_max`. Cache line size is returned in KiB from OCF's byte value.

The management runner stores a null-terminated path of step functions in `vbdev->mngt_ctx`. `vbdev_ocf_mngt_start()` rejects concurrent management with `-EBUSY`, initializes callback state, and invokes the first step. `vbdev_ocf_mngt_continue()` records status, advances to the next step, and finishes when the next entry is null. `vbdev_ocf_mngt_stop()` records errors, optionally switches to a rollback path, invokes the final callback, and clears the management context.

The central invariant is single active management operation per OCF vbdev. Step functions must eventually call continue or stop; rollback is selected only when a nonzero status and rollback path are present.
