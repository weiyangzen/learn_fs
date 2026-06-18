# sources/user-network-fs/nfs-ganesha/src/include/nfs_lib.h

## Purpose

`nfs_lib.h` exposes a minimal embeddable library interface for starting and reloading the Ganesha server from another process or test harness.

## Important APIs, Types, and Functions

It exports `nfs_config_path`, `nfs_libmain(config_path, log_path, debug_level)`, and `reread_config()`.

## Control Flow

An embedding caller sets or passes a config path/log path/debug level to `nfs_libmain`, which drives the normal prerequisite/config/package/server startup path. Later, `reread_config` triggers configuration reload behavior.

## State and Persistence Behavior

The library interface mutates global daemon state: config path, logging, exports, network services, caches, and worker threads. Reload persists only in process memory and configured runtime side effects.

## Dependencies and Integration Points

It is intentionally lightweight and integrates with `nfs_init.h`, config reload, logging, exports, and service lifecycle implementation.

## Risks and Test Signals

Risks include multiple `nfs_libmain` calls in one process, concurrent reloads, global path lifetime ownership, and shutdown limitations not declared here. Tests should embed-start with valid/invalid configs, verify log path/debug level application, perform reload success/failure, and check behavior when called twice or from multiple threads.
