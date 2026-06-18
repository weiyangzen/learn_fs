# sources/user-network-fs/samba/source4/smb_server/wscript_build

## Purpose
This Waf fragment defines the source4 SMB server service module and core SMB server subsystem, then recurses into SMB1 and SMB2 protocol subdirectories. It controls whether the NTVFS file server SMB service is built.

## Important APIs, Types, And Functions
It declares `service_smb` with source `service_smb.c`, generated `service_smb_proto.h`, service subsystem integration, init function `server_service_smb_init`, dependencies `SMB_SERVER netif shares samba-hostconfig cmdline`, and non-internal module visibility. It declares `SMB_SERVER` with sources `handle.c tcon.c session.c blob.c management.c smb_server.c`, generated `smb_server_proto.h`, and public dependencies `share LIBPACKET SMB_PROTOCOL SMB2_PROTOCOL`.

## Control Flow
At build time, Waf evaluates the module and subsystem declarations when `WITH_NTVFS_FILESERVER` is set. It then recurses into `smb` and `smb2`, where protocol-specific subsystem fragments extend the build graph.

## State And Persistence
This file affects build graph and generated prototype artifacts only. It has no runtime state.

## Dependencies And Integration Points
It ties service registration to the core SMB server subsystem and exposes both SMB1 and SMB2 protocol subsystems to the common server. It is a parent build node for the files researched in this subset.

## Risks And Test Signals
Risks include missing source files in subsystem lists, disabled builds omitting expected service registration, dependency order problems between `SMB_SERVER`, `SMB_PROTOCOL`, and `SMB2_PROTOCOL`, and stale autoproto output. Test signals are full configure/build with `WITH_NTVFS_FILESERVER`, disabled-feature builds, service module load tests, and incremental builds after changing exported functions.
