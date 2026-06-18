## sources/distributed-fs/xrootd/src/XrdSys/XrdSysHeaders.hh

Purpose: centralizes compatibility selection between modern `<iostream>` and old-style `<iostream.h>`.

Important APIs/types/functions: no functions or classes; includes `<iostream>` unless `HAVE_OLD_HDRS` is defined and `WIN32` is not, in which case it includes `<iostream.h>`.

Control flow: compile-time branch only.

State and persistence: none.

Dependencies and integration: included by legacy XrdSys/XrdSut files that write to `std::cerr` or need old compiler compatibility.

Risks: old-header support can mask namespace differences; modern code assumes `std::` names are available. The header is intentionally broad and can increase transitive dependency on iostream.

Test signals: compile with and without `HAVE_OLD_HDRS`, especially files using `std::cerr`, and verify Windows always uses modern include.
