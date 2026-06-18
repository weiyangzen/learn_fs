# sources/user-network-fs/nfs-ganesha/src/include/sss_nss_idmap.h

## Purpose
This header declares direct SSSD-backed passwd/group lookup helpers used as an alternative to libc NSS switching.

## Important APIs, Types, And Control Flow
It exposes `sss_nss_idmap__init`, `sss_nss_idmap__getpwnam`, `getpwuid`, `getgrnam`, `getgrgid`, and `getgrouplist` wrappers using caller-provided `passwd`/`group` buffers and result pointers.

## State And Persistence
Initialization likely sets process state for SSSD idmap access; lookup calls return transient buffer-backed records. No persistence is defined.

## Dependencies And Integration Points
It includes `<grp.h>` and `<pwd.h>` and is selected by `pwnam_wrappers` when SSSD implementation is configured. It feeds idmapper and uid2grp cache population.

## Risks And Test Signals
Risks include optional library availability, initialization failures, buffer sizing, domain-qualified names, and differences from NSS behavior. Tests should cover enabled/disabled SSSD builds, missing SSSD service, large group lists, unknown identities, and concurrent lookup calls.
