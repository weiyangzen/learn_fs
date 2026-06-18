# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/Makefile

Builds the `nvmecontrol` utility and its module subdirectories.

Key contents:
- Program: `nvmecontrol`.
- Adds command sources including command framework, fabrics, firmware, format, identify, logpage, namespace, passthrough, power, reconnect, reset, reservation, sanitize, selftest, telemetry, and utility files.
- Includes sys NVMe path with `.PATH: ${SRCTOP}/sys/dev/nvme`.
- Links with `nvmf`, `sbuf`, and `util`.
- Uses `-rdynamic`, enabling dynamically loaded modules to resolve symbols in the main executable.
- Descends into `modules`; tests are optional via `SUBDIR.${MK_TESTS}+= tests`.

Research notes:
- The listed group includes core command files and logpage modules, but not every source referenced by the Makefile.
