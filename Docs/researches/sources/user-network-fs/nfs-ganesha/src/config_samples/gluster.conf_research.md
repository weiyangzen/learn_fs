# sources/user-network-fs/nfs-ganesha/src/config_samples/gluster.conf

## Purpose

`gluster.conf` is a minimal export sample for serving a Gluster volume through NFS-Ganesha.

## Important APIs, Types, and Functions

It exercises an `EXPORT` block with `Export_Id`, `Path`, `Pseudo`, `Access_Type`, `Squash`, `SecType`, and nested `FSAL` fields `Name`, `Hostname`, `Volume`, `enable_upcall`, and `Transport`.

## Control Flow

The sample defines one export of `/testvol` at pseudo path `/testvol`, grants read/write access, disables root squashing, selects sys security, and binds the export to FSAL `GLUSTER` on localhost volume `testvol` over TCP.

## State and Persistence Behavior

Runtime state is in the Gluster volume and Ganesha export table. The config enables upcalls, so cache coherency depends on Gluster notification support.

## Dependencies and Integration Points

It depends on FSAL_GLUSTER, Gluster client libraries, export handling, MDCACHE/upcall integration, and NFS security flavor parsing.

## Risks and Edge Cases

`No_Root_Squash` is permissive and should be reviewed before production use. The sample uses localhost and a fixed volume name, so operators must adjust deployment-specific values. RDMA transport is mentioned but not selected.

## Test Signals

Syntax validation should pass. Runtime validation requires a Gluster volume named `testvol`, FSAL_GLUSTER built, NFS mount of `/testvol`, and upcall behavior tests when enabled.
