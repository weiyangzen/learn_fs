# sources/user-network-fs/nfs-ganesha/src/include/rados_grace.h

## Purpose
This header declares Ceph RADOS-backed NFS grace-period coordination APIs used by clustered Ganesha instances.

## Important APIs, Types, And Control Flow
It defines default pool/object names `nfs-ganesha` and `grace`. Bulk operations include `rados_grace_create`, `dump`, `epochs`, `enforcing_toggle`, `enforcing_check`, `join_bulk`, `lift_bulk`, `add`, and `member_bulk`. Inline single-node wrappers build a one-element `nodeids` array for enforcing on/off, join, lift, and member checks.

## State And Persistence
Grace state persists in a RADOS object addressed by `rados_ioctx_t` and object id. The APIs track current/recovery epochs, enforcing status, and cluster membership for node ids.

## Dependencies And Integration Points
The header assumes Ceph `rados_ioctx_t` is visible from prior includes and uses `<stdio.h>` for dumping. It integrates with NFSv4 recovery backends and grace enforcement in SAL.

## Risks And Test Signals
Distributed state consistency, partial bulk updates, epoch races, and object creation failures are the key risks. Tests should simulate join/lift/enforcing transitions, multiple nodes, missing RADOS objects, epoch reads, and recovery behavior under RADOS errors.
