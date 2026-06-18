# File Research: sources/virtualization/spdk/module/bdev/error/vbdev_error.c

## Purpose
Implements SPDK's test-oriented error-injection virtual bdev. It wraps an existing bdev as `EE_<base>` and can inject failures, NVMe status failures, NOMEM, pending I/O, or data corruption for selected I/O types.

## Main Entry Points
- `vbdev_error_create()` records requested configuration and attempts to construct an error partition over the base bdev.
- `vbdev_error_delete()` unregisters the named error bdev.
- `vbdev_error_inject_error()` updates per-I/O-type injection rules.
- `vbdev_error_resume_pending()` clears pending injection counts and resubmits held I/O.
- `vbdev_error_examine()` creates configured error bdevs when their base bdevs are examined.
- `vbdev_error_config_json()` emits replayable `bdev_error_create` RPC config.

## Internal Mechanics
Each `error_disk` is a `spdk_bdev_part` with an `error_vector` indexed by bdev I/O type up to RESET. Each `error_channel` tracks in-flight I/O and a queue of pending injected I/O. `vbdev_error_get_error_type()` only injects READ, WRITE, UNMAP, and FLUSH, waits until `io_inflight >= error_qd`, and atomically decrements `error_num`.

The request path handles RESET specially by iterating all channels and aborting `pending_ios`. Failure injection completes immediately with normal bdev, NVMe, or NOMEM status. Pending injection queues the bdev I/O context without submitting to the base. Corrupt-data injection XORs one byte at `corrupt_offset`: writes are corrupted before forwarding, while reads are corrupted after successful base completion. Normal and corrupt I/O are forwarded through `spdk_bdev_part_submit_request_ext()`.

Configuration is maintained separately in `g_error_config` so create requests can survive base-bdev absence and be replayed during examine. Hotremove delegates to `spdk_bdev_part_base_hotremove()`.

## Dependencies
Uses SPDK bdev module and partition helpers, JSON config writers, UUID handling, pthread mutexes, atomics, and SPDK TAILQ/channel iteration utilities.

## Risks and Notes
`opts->io_type` is used as an array index for the targeted case; callers must pass either the special all/reset values or a valid bdev I/O type. Pending I/O lifetime depends on reset/resume paths removing the stored driver context exactly once. `vbdev_error_resume_pending()` sends resubmit messages to `spdk_get_thread()` from the channel-iteration callback, so thread context matters when reasoning about resubmission ordering.
