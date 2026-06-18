# File Research: sources/os/linux/linux-stable/fs/nfsd/netlink.c

## Summary
Auto-generated generic netlink family definition for NFSD control operations.

## Main APIs
Exports `nfsd_nl_family` and nla policies for socket and version nested attributes.

## Behavior
Registers split ops for RPC status dump, thread set/get, protocol version set/get, listener set/get, and pool mode set/get. Admin permission is required for mutating commands. Policies validate nested socket address/transport name, protocol major/minor/enabled fields, server thread/grace/lease/scope/min-thread/fh-key fields, and pool mode.

## Risks
This file is generated from `Documentation/netlink/specs/nfsd.yaml`; manual edits should not be made here. Semantic behavior lives in the handlers declared in `netlink.h`.
