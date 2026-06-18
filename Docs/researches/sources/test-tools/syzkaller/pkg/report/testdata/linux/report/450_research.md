# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/450

Purpose: golden fixture for a boot-time general protection fault in the DMA/SCSI initialization path. Expected title is `general protection fault in dma_direct_max_mapping_size`, alternate title is `bad-access in dma_direct_max_mapping_size`, type is `DoS`, and `PANICKED: Y`.

Important APIs, types, and functions: parser APIs include GPF detection, bad-access alternate generation, and panic recognition. Kernel frames include `dma_direct_max_mapping_size`, `dma_max_mapping_size`, `__scsi_init_queue`, `scsi_mq_alloc_queue`, `scsi_alloc_sdev`, `scsi_probe_and_add_lun`, `__scsi_scan_target`, `do_scan_async`, `async_run_entry_fn`, and workqueue execution.

Control flow: the file contains a long boot log with subsystem initialization noise before the crash. The actual report begins around the KASAN GPF lines in `kworker/u4:1` on `events_unbound async_run_entry_fn`. The parser must ignore earlier boot warnings and device registration chatter, select the DMA direct mapping RIP, follow the SCSI scan call trace, and set `Panicked` from the fatal-exception tail.

State and persistence behavior: static boot-log fixture persists interleaved kobject messages and repeated RIP/register blocks. No mutable state exists, but the file protects parser start-boundary and noise handling.

Dependencies and integration points: depends on Linux console-prefix stripping with `[ T...]` contexts, GPF detection, KASAN noise tolerance, guilty-frame selection, and panic matching. It integrates DMA mapping, SCSI scan, async workqueue, and boot-time device discovery paths.

Risks: the long prelude includes a `WARNING: workqueue cpumask...` that should not become the title. Interleaved device/kobject logs in the middle of the call trace can break simplistic contiguous-stack parsers.

Test signals: `general protection fault: 0000 [#1] PREEMPT SMP KASAN`, `RIP: 0010:dma_direct_max_mapping_size+0x7c/0x1a7`, `Workqueue: events_unbound async_run_entry_fn`, SCSI allocation frames, and `Kernel panic - not syncing: Fatal exception`.
