# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_target.h

## Purpose
Defines the `/dev/overlay` varpd ioctl interface for associating userland overlay target resolution services with kernel overlay links, servicing dynamic lookups, injecting/resending packets, listing overlay devices, and manipulating target caches.

## Main Interfaces
- `overlay_target_point_t`: resolved endpoint with Ethernet address, IPv6 address, and port.
- Base ioctl family `OVERLAY_TARG_IOCTL`.
- Device state ioctls:
  - `OVERLAY_TARG_INFO`
  - `OVERLAY_TARG_ASSOCIATE`
  - `OVERLAY_TARG_DISASSOCIATE`
  - `OVERLAY_TARG_DEGRADE`
  - `OVERLAY_TARG_RESTORE`
- Lookup/response packet ioctls:
  - `OVERLAY_TARG_LOOKUP`
  - `OVERLAY_TARG_RESPOND`
  - `OVERLAY_TARG_DROP`
  - `OVERLAY_TARG_INJECT`
  - `OVERLAY_TARG_PKT`
  - `OVERLAY_TARG_RESEND`
- List/cache ioctls:
  - `OVERLAY_TARG_LIST`
  - `OVERLAY_TARG_CACHE_GET`
  - `OVERLAY_TARG_CACHE_SET`
  - `OVERLAY_TARG_CACHE_REMOVE`
  - `OVERLAY_TARG_CACHE_FLUSH`
  - `OVERLAY_TARG_CACHE_ITER`
- Main ioctl payloads:
  - `overlay_targ_info_t`
  - `overlay_targ_associate_t`
  - `overlay_targ_degrade_t`
  - `overlay_targ_id_t`
  - `overlay_targ_lookup_t`
  - `overlay_targ_resp_t`
  - `overlay_targ_pkt_t`
  - `overlay_targ_list_t`
  - `overlay_targ_cache_entry_t`
  - `overlay_targ_cache_t`
  - `overlay_targ_cache_iter_t`
- Kernel 32-bit compatibility structure:
  - `overlay_targ_pkt32_t`

## Dependencies And Relationships
Includes datalink, Ethernet, IPv6, and overlay-common definitions. This is the user/kernel contract used by `varpd` and the overlay target-cache machinery.

## Research Notes
Dynamic lookup is designed around userland threads blocking in `OVERLAY_TARG_LOOKUP` for about one second, then responding through separate ioctls. Cache iteration is bounded by `OVERLAY_TARGET_ITER_MAX` to cap kernel allocation.
