# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_af_thr.h

This Solaris-only RDSv3 header declares asynchronous/soft-CQ thread and HCA affinity group APIs.

Core definitions:
- Opaque `rdsv3_af_grp_t` and `rdsv3_af_thr_t` represent HCA affinity groups and async worker threads.
- Drain callbacks take a single private data pointer.
- Creation flags can bind HCA, interrupt, or worker execution to CPUs.
- APIs initialize the AF subsystem, create/destroy/draw HCA groups, retrieve an IBT scheduler handle, create normal or interrupt-backed AF threads, destroy threads, and fire threads.

Risk-sensitive invariants:
- CPU binding flags influence CQ and worker placement for performance.
- Interrupt-backed thread creation receives an IBT CQ handle, tying affinity to completion delivery.
