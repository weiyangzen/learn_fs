# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi.h

DDI-conforming driver helper header. It undefines selected kernel macros and replaces them with driver-callable functions or DDI-safe macros for parameters, device numbers, page/block conversions, STREAMS helpers, buffers, and privileges.

Key elements:
- Comments warn drivers to include `sys/ddi.h` after headers that may define macros being undefined here.
- Redefines `min` and `max` as unsigned-expression macros so drivers avoid signed-only kernel functions.
- Defines `drv_getparm()` parameter selectors such as time, process, process group, lbolt, syscall counters, parent/session IDs, and credentials.
- Declares DDI driver utility functions for get/set parameter, microsecond waits, hz/usec conversion, delay, timed waits, major-number conversion, and privilege checking.
- Undefines device-number macros from `sysmacros.h` and declares function forms for external/internal major/minor extraction, device construction, compression, and expansion.
- Undefines block/page conversion macros and declares function forms for `btop`, `btopr`, and `ptob`.
- Undefines STREAMS queue/data macros and declares function forms for `OTHERQ`, `RD`, `WR`, `SAMESTR`, and `datamsg`.
- Declares buffer-header allocation/free helpers `getrbuf()` and `freerbuf()`.
- Kernel-only portion defines `NOPAGE`, typedefs `ppid_t`, and declares `kvtoppid()` and `qassociate()`.

Dependencies:
- Includes system types, map, buffer, uio, and STREAMS headers.
- Consumed broadly by DDI-compliant drivers to get stable function interfaces instead of private macros.

Research notes:
- This header deliberately changes macro/function binding depending on include order; incorrect ordering can alter compilation.
- It is compatibility glue between old macro-heavy kernel headers and the DDI driver ABI.
