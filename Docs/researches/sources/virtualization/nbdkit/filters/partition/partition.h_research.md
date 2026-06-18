# File Research: sources/virtualization/nbdkit/filters/partition/partition.h

This internal header defines sector-size constants (`512`, `4096`, default `512`), declares global `partnum` and `sector_size`, and exposes the MBR/GPT helper entry points used by `partition.c`.

It includes the nbdkit filter API because the helper signatures take `nbdkit_next *` for backend reads. The header is limited to the partition filter module and has no public API role outside this filter.
