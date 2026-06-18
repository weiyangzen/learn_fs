# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_af_thr_impl.h

This Solaris-only private RDSv3 AF-thread header defines the implementation structures for CPU/MSI-X affinity and worker state.

Core definitions:
- `ddi_intr_set_affinity` is mapped to `set_intr_affinity`.
- Combined `SCQ_BIND_CPU` binds HCA and worker CPUs.
- Constants define maximum connections per HCA group, per-connection CPU count, CPU/MSI-X pool sizes, and CPU flag bits.
- Static CPU and MSI-X pools track available binding candidates.
- `rdsv3_af_grp_s` stores HCA handle, scheduler handle, assigned HCA CPU, per-connection CPU pool, and next index.
- `rdsv3_af_thr_s` stores lock/CV, worker thread, callback data, CPU binding, state flags, creation flags, drain callback, group pointer, and interrupt handle.
- State flags track processing, bound, armed, and condemned states.

Risk-sensitive invariants:
- Worker state is protected by `aft_lock`.
- Condemned state coordinates teardown with worker wakeups.
- CPU pool sizing caps affinity assignment at 128 CPUs/MSI-X entries.
