# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/info.h

This OFED-derived RDSv3 info header defines the generic snapshot/copy interface used by RDSv3 diagnostic ioctls.

Core definitions:
- `rdsv3_info_iterator` carries a user destination address and current byte offset.
- `rdsv3_info_lengths` reports number of records and bytes per record.
- `rdsv3_info_func` callbacks describe available snapshot size and copy data when the user buffer is large enough.
- `rdsv3_info_copy` wraps `ddi_copyout()` and advances the iterator offset.
- Register/deregister functions attach info callbacks to option names; `rdsv3_info_ioctl()` serves user info requests.

Risk-sensitive invariants:
- Callers infer whether a snapshot was copied by comparing requested lengths to available lengths.
- `rdsv3_info_copy` ignores the `ddi_copyout()` return value in the macro, so caller-side size validation is important.
