# File Research: sources/teaching/minix/minix/drivers/storage/filter/sum.c

## Purpose

Implements the filter driver's checksum-aware logical-to-physical transfer layer. It maps user-visible logical sectors into a physical layout where groups of data sectors are followed by checksum sectors, computes or verifies checksums, and optionally verifies writes by reading data back from the underlying disk drivers.

## Main Entry Points

- `sum_init()`: allocates static backing buffers for expanded I/O and write-readback checks.
- `transfer()`: central read/write path; expands logical data into checksum layout for writes, collapses checksum layout for reads, and delegates actual I/O to `read_write()`.
- `convert()`: converts raw disk size to user-visible size by subtracting checksum sectors.
- `calc_sum()`: computes the configured checksum type: nil, XOR, CRC32, or MD5.
- `make_sum()` / `check_sum()`: generate or validate checksum sectors across expanded transfer buffers.
- `check_write()`: reads written data back from the main and optional mirror disk, then compares it to the expanded write buffer.
- `expand()` / `collapse()`: convert between contiguous logical data and interspersed checksum layout.

## Control Flow And State

The layout macros define groups of `NR_SUM_SEC` logical data sectors followed by one checksum sector. `transfer()` short-circuits directly to `read_write()` if checksum layout is disabled. Otherwise it computes the physical start offset, expands the request into `ext_buffer`, and performs one lower-level I/O over the physical span.

For writes, the code copies user data into the expanded layout, reads partial checksum/data tails where needed, updates checksums, writes the expanded data, optionally read-verifies, and returns the logical byte count through `collapse_size()`. For reads, it reads expanded data, verifies checksum sectors, and copies only logical sectors back to the caller.

`make_sum()` handles partial group writes carefully: it reads existing checksum sectors and any gap data so unrelated sectors in the same checksum group are preserved. `check_sum()` walks the expanded buffer group by group and returns `RET_REDO` through `bad_driver()` behavior on checksum failure.

## Dependencies

Depends on filter globals and policy macros from `inc.h`, checksum implementations from `crc.h` and `md5.h`, `flt_malloc()`/`flt_free()`, `read_write()`, and lower-driver failure handling through `bad_driver()`.

## Risks

Correctness depends on sector-aligned requests and exact agreement between `LOG2PHYS()`, `SEC2SUM_NR()`, `expand_sizes()`, and `collapse_size()`. Partial writes are the highest-risk path because they preserve existing checksum sectors and gap data. `check_write()` has early returns after compare failures without freeing readback buffers, which is safe only if the process is expected to continue with bounded static buffers or abort/retry soon after. The checksum code also stores sector numbers through `unsigned long *`, so checksum byte layout is architecture-sensitive.
