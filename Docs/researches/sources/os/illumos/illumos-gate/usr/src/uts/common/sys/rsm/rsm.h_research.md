# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm.h

## Role

`rsm.h` defines kernel-agent ioctl command groups, debug categories, internal ioctl payload structures, polling/event payloads, and remote messaging structures for Remote Shared Memory.

## Ioctl Surface

Command groups cover controller, export segment, import segment, queue, topology, barrier, error count, bell, iovec, and map-address operations. Specific ioctls include controller attributes, barrier info/open/order/close/check, export create/bind/rebind/unbind/publish/republish/unpublish, import connect/disconnect, topology size/data, getv/putv, ring bell, consume event, and address mapping.

`RSM_IOCTL_CMDGRP()` extracts command groups.

## Kernel-Agent Structures

The file defines:
- internal controller attributes with controller address.
- kernel-agent iovec and scatter-gather structures, including 32-bit variants.
- poll event and consume-event messages.
- generic `rsm_ioctlmsg_t` with controller name, argument buffers, virtual address, offsets, segment key, ACL, node/hardware address, permission, barrier, generation number, and resource number.

## Remote Messaging

RSM IPC messages use `rsmipc_cookie_t` plus typed message headers. Message types cover segment connect/disconnect, importing/not-importing, reply, bell, republish, suspend/resume, send-queue readiness, and credits.

Request, control, and reply messages carry segment keys, permissions, adapter hardware addresses, cookies, credits, segment metadata, and owner/mode fields.

## Research Notes

This header is the bridge between RSM user APIs, the kernel agent, and remote-node messaging. ABI-sensitive areas include ioctl numeric grouping, 32-bit structure translation, and the contiguous residual-count/flags assumption in scatter-gather structures.
