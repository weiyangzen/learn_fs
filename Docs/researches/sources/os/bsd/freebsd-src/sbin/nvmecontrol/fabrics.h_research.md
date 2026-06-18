# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/fabrics.h

Header for shared NVMe over Fabrics command helpers.

Key contents:
- Declares address parsing, controller ID parsing, default HostNQN generation, discovery-log-entry initialization, discovery admin-queue connection, NVM queue connection, and queue disconnect helpers.
- Documents ownership for parsed address buffers via `tofree`.
- Documents that `connect_nvm_queues()` returns sysexits-style failure codes.

Research notes:
- This is the shared interface between user commands and lower-level libnvmf connection setup.
