# File Research: sources/virtualization/qemu/hw/virtio/virtio-rng.c

## Purpose
Core virtio RNG device implementation. It supplies entropy from a QEMU RNG backend to guest-provided virtqueue buffers with rate limiting.

## Main Responsibilities
- Checks guest readiness using virtqueue readiness and `VIRTIO_CONFIG_S_DRIVER_OK`.
- Computes guest-requested input capacity using `virtqueue_get_avail_bytes()`.
- Requests entropy from the configured `RngBackend` and copies returned bytes into guest input SG buffers.
- Pushes completed buffers and notifies the guest.
- Implements quota/rate limiting using `max-bytes`, `period`, `quota_remaining`, and a virtual-clock timer.
- Retries processing on VM run-state changes and status changes.
- Creates a default builtin RNG backend when no `rng` property is supplied.
- Initializes virtio device ID `VIRTIO_ID_RNG` with one 8-entry virtqueue.
- Registers VMState containing generic virtio device state.

## Properties
- `max-bytes`: maximum entropy bytes per period, default `INT64_MAX`.
- `period`: rate-limit period in milliseconds, default `1 << 16`.
- `rng`: link to an `RngBackend`; if absent, a builtin backend child is created.

## Control Flow
- Guest kicks queue -> `handle_input()` -> `virtio_rng_process()`.
- `virtio_rng_process()` checks readiness, arms timer when needed, limits requested size by quota, and calls `rng_backend_request_entropy()`.
- Backend returns entropy -> `chr_read()` fills guest buffers, reduces quota, notifies guest, and continues processing if the queue remains non-empty.
- Timer expiry -> `check_rate_limit()` replenishes quota and resumes processing.

## Integration Points
- Uses QEMU runstate to avoid modifying virtqueues while CPUs are stopped.
- Uses QOM user-creatable completion for the default RNG backend.
- Uses virtio class callbacks for realize, unrealize, feature passthrough, and status update.

## Notable Constraints and Risks
- Rejects non-positive `period`.
- Rejects `max-bytes == 0` and values beyond `INT64_MAX`, compensating for property parsing limitations.
- Entropy delivery is paused when the VM is not running, then retried on resume.
- Rate limiting is based on virtual time, not wall-clock time.

## Filesystem/Storage Relevance
No direct filesystem role. It is part of the same virtio device family and demonstrates queue, runstate, migration, and backend-link patterns shared with storage-oriented virtio devices.
