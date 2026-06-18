# File Research: sources/os/linux/linux/block/blk-mq-cpumap.c

## Summary
Provides helper functions for sizing and building CPU-to-hardware-queue maps for blk-mq devices.

## Main Responsibilities
- Calculate queue counts from possible or online CPU masks.
- Evenly map CPUs to hardware queues.
- Map queues from device/bus IRQ affinity when available.
- Find a representative NUMA node for a hardware queue.

## Key APIs
- `blk_mq_num_possible_queues()`.
- `blk_mq_num_online_queues()`.
- `blk_mq_map_queues()`.
- `blk_mq_hw_queue_to_node()`.
- `blk_mq_map_hw_queues()`.

## Important Behavior
`blk_mq_map_queues()` uses `group_cpus_evenly()` to spread CPUs across the requested number of queues. If grouping fails, every possible CPU maps to `queue_offset`.

`blk_mq_map_hw_queues()` first asks the device bus for IRQ affinity masks. If the bus lacks `irq_get_affinity()` or any queue has no mask, it falls back to the generic even mapping.

## State and Synchronization
The file only fills caller-provided `struct blk_mq_queue_map` arrays during queue setup. There is no persistent state.

## Risks
Fallback behavior is coarse and may place all CPUs on one queue if CPU grouping allocation fails. Reverse node lookup is linear over possible CPUs and intended only for initialization.
