# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/xencomm.h

Purpose: Xen public xencomm descriptor header. It defines a scatter/gather descriptor for platforms where the hypervisor needs physical addresses backing a virtually contiguous memory area.

Key interfaces:
- `XENCOMM_MAGIC`, `XENCOMM_INVALID`.
- `struct xencomm_desc` with `magic`, `nr_addrs`, and flexible `address[]`.

Integration notes: Standalone header, no includes in the file itself.

Risk/attention points: Consumers must allocate enough trailing address entries and fill physical addresses in hypervisor-expected order.
