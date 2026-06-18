# File Research: sources/os/bsd/dragonflybsd/sys/sys/memrange.h

Defines `/dev/mem` memory range attribute ABI. User structures `mem_range_desc` and `mem_range_op` describe base, length, cache/write attributes, owner, and set/remove operations. Ioctls are `MEMRANGE_GET` and `MEMRANGE_SET`.

Kernel section declares `mem_range_ops`, `mem_range_softc`, global softc, get/set helpers, AP init, and I/O privilege helpers. Relevant to low-level storage/device mappings where cache attributes matter.
