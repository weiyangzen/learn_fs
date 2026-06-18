# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fasttrap_impl.h

## Role

`fasttrap_impl.h` is the private kernel implementation header for the DTrace fasttrap provider. It defines provider/process/probe/tracepoint state and ISA hooks used to instrument user processes.

## Model

The file documents the fasttrap object model:

- A process can have multiple providers, including pid and USDT providers.
- Providers for one process share a `fasttrap_proc_t`, whose active-provider count determines whether it is active or defunct.
- Probes contain tuples of fasttrap ids and tracepoints.
- Tracepoints represent actual instrumented PCs and hold pre/post probe id lists.
- Tracepoints can be shared and ownership can move between probes when probes are disabled.

## Structures

- `fasttrap_proc_t` stores pid, active and extant provider counts, lock, and hash-chain link.
- `fasttrap_provider_t` stores pid, provider name, DTrace provider id, removal/retirement marks, locks, enabled probe/create/meta counts, shared process pointer, and hash-chain link.
- `fasttrap_id_t` links enabled probe ids to tracepoints and records probe type.
- `fasttrap_id_tp_t` combines an id and tracepoint pointer.
- `fasttrap_probe_t` stores DTrace id, pid, provider, function address/size, generation, tracepoint count, argument type/translation data, enabled flag, and flexible tracepoint tuple array.
- `fasttrap_tracepoint_t` stores associated process, PC, pid, ISA-specific tracepoint state, pre/post id lists, and hash link.
- `fasttrap_bucket_t` pads each hash bucket to 64 bytes around the lock and data pointer.
- `fasttrap_hash_t` stores power-of-two bucket count, mask, and table.

## Hooks

The header maps internal copy/userword operations to kernel primitives, declares `fasttrap_sigtrap()`, global `fasttrap_probe_id` and `fasttrap_tpoints`, hash index macro, ISA-required tracepoint init/install/remove, pid/return probe entry points, and pid/USDT argument fetchers.
