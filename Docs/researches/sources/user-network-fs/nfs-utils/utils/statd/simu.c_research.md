## sources/user-network-fs/nfs-utils/utils/statd/simu.c

Purpose: Implements the `SM_SIMU_CRASH` RPC service for test/simulation builds.

Important APIs/types/functions: `sm_simu_crash_1_svc` validates caller address/port, calls `my_svc_exit`, and clears the runtime monitor list.

Control flow: The procedure accepts only IPv4 loopback callers from privileged ports. Accepted calls stop the custom service loop and kill the runtime notify list.

State and persistence: Mutates only in-memory runtime list and service-loop stop flag. It does not retire NSM state files.

Dependencies and integration: Built for simulation support, depends on `nfs_getrpccaller`, `nfs_is_v4_loopback`, `nfs_get_port`, and `notlist`.

Risks and test signals: Security relies on loopback plus privileged-port checks. Tests should cover non-local callers, unprivileged local port rejection, list cleanup, and service-loop exit.
