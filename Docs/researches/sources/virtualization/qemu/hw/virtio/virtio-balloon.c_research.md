# File Research: sources/virtualization/qemu/hw/virtio/virtio-balloon.c

## Purpose
Implements the virtio balloon device: inflation/deflation, guest statistics, free-page hinting, free-page reporting, page poison handling, QMP balloon target integration, reset behavior, and VMState subsections.

## Key Elements
- Inflate/deflate: `virtio_balloon_handle_output()` reads PFNs from inflate/deflate queues, validates RAM sections, and calls `balloon_inflate_page()` or `balloon_deflate_page()`.
- Page discard: `balloon_inflate_page()` discards whole host pages immediately when host page size equals virtio balloon page size, or tracks partially ballooned host pages with a bitmap until a whole host page can be discarded.
- Deflate hinting: `balloon_deflate_page()` issues `QEMU_MADV_WILLNEED` for the containing host page.
- Stats: `balloon_stat_names`, `reset_stats()`, `virtio_balloon_receive_stats()`, and QOM properties expose guest stats and polling interval, using a timer to prompt the stats virtqueue.
- Free-page reporting: `virtio_balloon_handle_report()` discards guest-reported free page ranges from writable RAM if discards are not inhibited and page poison is not active.
- Free-page hinting: `get_free_page_hints()`, `virtio_ballloon_get_free_page_hints()`, and migration notifier callbacks coordinate hinting through an IOThread and precopy migration phases.
- Config: `virtio_balloon_get_config()` and `virtio_balloon_set_config()` expose `num_pages`, `actual`, free-page command IDs, and `poison_val`, with config size depending on negotiated host features.
- Realize/unrealize: `virtio_balloon_device_realize()` registers the global balloon handler, creates queues, validates that free-page hinting has an IOThread, installs migration notifier/BH as needed, and registers resettable state.
- VMState: saves `num_pages`, `actual`, and optional free-page-hint/page-poison subsections.

## Dependencies
Uses QEMU virtio core/accessors, RAMBlock discard APIs, memory-region lookup, QAPI balloon events, migration notifiers, reset framework, IOThread/AIO BHs, timers, QOM properties, and machine memory sizing.

## Behavior/Risks
- Ballooning is inhibited when RAM discard is disabled, incoming postcopy is active, or background snapshotting is active.
- Free-page hinting is skipped when postcopy RAM is possible because hinted pages are removed from the dirty bitmap.
- Backing page sizes larger than 4 KiB are warned as potentially unreliable and require partial-page tracking.
- Only one balloon handler is supported.
- `free-page-hint` requires an `iothread`; realization fails otherwise.
- Reset stops free-page hinting and returns any saved stats queue element; wakeup reset intentionally preserves stats.
