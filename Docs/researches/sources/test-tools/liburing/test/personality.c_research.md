# sources/test-tools/liburing/test/personality.c

Purpose: verifies io_uring personality registration executes operations under saved credentials, including linked operations, and rejects invalid personality ids.

Important APIs/types/functions: `io_uring_register_personality`, `io_uring_unregister_personality`, `sqe->personality`, `seteuid`, `geteuid`, `io_uring_prep_openat`, `IOSQE_IO_LINK`, `FNAME=/tmp/.tmp.access`, and `USE_UID=1000`.

Control flow: root-only main registers current credentials, creates a 0600 file, verifies current root can open it, switches effective uid to 1000, verifies normal open fails with `-EACCES`, verifies open with registered personality succeeds both standalone and after a linked NOP, restores euid 0, unregisters, then checks invalid personality use and unregister return `-EINVAL`.

State and persistence behavior: creates `/tmp/.tmp.access` and removes it. Stores one registered credential id in the ring until unregistered.

Dependencies and integration points: requires root and a usable UID 1000. `-EINVAL` personality registration skips unsupported kernels.

Risks and test signals: failures are credential leakage, inability to use registered credentials in linked chains, invalid ids accepted, or failure to restore/unregister credentials.
