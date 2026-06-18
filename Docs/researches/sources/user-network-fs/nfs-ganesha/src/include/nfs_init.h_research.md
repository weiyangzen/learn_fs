# sources/user-network-fs/nfs-ganesha/src/include/nfs_init.h

## Purpose

`nfs_init.h` declares server prerequisite initialization, config loading, package startup, service start, init-completion synchronization, worker RPC validators, and a malloc behavior guard.

## Important APIs, Types, and Functions

`nfs_start_info_t` carries startup flags for default config dump, low-watermark trigger, and capability dropping. `struct nfs_init` provides mutex/condition/init-complete fields. APIs include `nfs_prereq_init_mutexes`, `nfs_init_init`, `nfs_init_cleanup`, `nfs_init_complete`, `nfs_init_wait`, `nfs_init_wait_timeout`, `nfs_prereq_init`, `nfs_prereq_destroy`, `nfs_set_param_from_conf`, `init_server_pkgs`, `nfsv4_init_params`, and `nfs_start`. `nfs_check_malloc` fatally validates `malloc(0)` and `calloc(0,0)` behavior.

## Control Flow

Main/library startup initializes prerequisites, parses config, initializes packages and NFSv4 parameters, starts services, and signals init completion. Other threads can wait for completion. Worker validation functions screen incoming RPCs for NFS, MOUNT, NLM, RQUOTA, NFSACL, and RDMA when compiled.

## State and Persistence Behavior

State includes init synchronization, DBus thread ID, config-derived runtime parameters, and started service packages. Persistent effects are pid/log/config side effects and network listeners.

## Dependencies and Integration Points

It depends on `log.h` and `nfs_core.h`, and integrates with main daemon startup, library embedding, DBus, worker dispatch, optional protocols, and capability management.

## Risks and Test Signals

Risks include init wait deadlocks, timeout misuse, partial-start cleanup gaps, allocator assumptions on unusual libc implementations, config reload divergence, and optional validator compile paths. Tests should run prerequisite init/destroy cycles, wait/timeout behavior, config parse failures, malloc guard on supported platforms, service startup smoke tests, and validator behavior for each enabled RPC program.
