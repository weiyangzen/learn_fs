<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/err_inject.c -->
# sources/user-network-fs/nfs-ganesha/src/support/err_inject.c

## Purpose
This file is a dormant error-injection support module. It currently only compiles two global delay variables when included by the build; the intended SNMP administration accessors and registration are disabled under `#if 0`.

## Important APIs, Types, and Functions
Active symbols are `int worker_delay_time` and `int next_worker_delay_time`. Disabled code contains `getErrInjectInteger`, `setErrInjectInteger`, an `snmp_error_injection` table with `worker_delay` and `next_worker_delay`, and `init_error_injector`.

## Control Flow
There is no active control flow beyond global variable definition. If the disabled block were re-enabled, getters/setters would map option 0 to `worker_delay_time` and option 1 to `next_worker_delay_time`, and initialization would register the table with SNMP administration.

## State and Persistence Behavior
The two active globals are mutable process state and are not persisted. No locking or atomic access is provided in this file.

## Dependencies and Integration Points
The file includes core NFS-Ganesha headers, logging, export/tool headers, pthread/time/stat headers, and is conditionally added to the `support` object library when `ERROR_INJECTION` is enabled. The disabled code references legacy SNMP admin types and registration functions.

## Risks and Test Signals
Risks include dead code drifting away from current admin infrastructure, unsynchronized global variables if other modules read/write them, and builds enabling `ERROR_INJECTION` getting symbols that are not controllable. Test signals are compile tests with `ERROR_INJECTION=ON`, searches for active references to the delay globals, and any future admin/DBus replacement tests that set delays and verify worker behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/err_inject.c -->
