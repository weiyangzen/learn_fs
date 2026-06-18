# File Research: sources/os/linux/linux/mm/bpf_memcontrol.c

## Purpose
Registers BPF kfuncs that let BPF programs acquire memory cgroup references and read memory-controller statistics, events, usage, and page-state counters.

## Main Interfaces
- Reference helpers: `bpf_get_root_mem_cgroup()`, `bpf_get_mem_cgroup()`, `bpf_put_mem_cgroup()`.
- Read helpers: `bpf_mem_cgroup_vm_events()`, `bpf_mem_cgroup_usage()`, `bpf_mem_cgroup_memory_events()`, `bpf_mem_cgroup_page_state()`.
- Maintenance helper: `bpf_mem_cgroup_flush_stats()`.
- Registration: `bpf_memcontrol_init()` registers the BTF kfunc ID set for `BPF_PROG_TYPE_UNSPEC`.

## Control Flow
The getter for arbitrary CSS accepts a CSS from any controller, resolves the corresponding memcg CSS through the cgroup’s subsystem array when necessary, and uses `css_tryget()` to provide acquire semantics. Counter helpers validate event/stat indexes before reading memcg counters. The kfunc set annotates acquire, release, nullable return, RCU, and sleepable semantics for verifier use.

## State And Synchronization
Uses CSS reference counting for acquired memcgs and RCU while translating non-memcg CSS values to the memcg subsystem CSS. Stats flushing may sleep and is marked `KF_SLEEPABLE`.

## Integration Points
Connects memcg internals, BPF kfunc registration, BTF ID metadata, VM event/stat validation helpers, page counters, and memcg rstat flushing.

## Risks And Review Focus
- Verifier annotations must match actual lifetime and sleepability behavior.
- Root memcg is returned with acquire semantics despite not needing a ref, so `bpf_put_mem_cgroup()` remains valid.
- Invalid event/stat indexes intentionally return `(unsigned long)-1`.
