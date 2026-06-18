# File Research: sources/virtualization/spdk/module/bdev/delay/vbdev_delay.h

This header declares the delay vbdev management API and includes the public delay module enum definitions from `spdk/module/bdev/delay.h`. `create_delay_disk()` creates a delay vbdev over a base bdev with UUID and average/p99 read/write latency values. `delete_delay_disk()` unregisters by virtual bdev name using an SPDK unregister callback.

`vbdev_delay_update_latency_value()` updates one latency class at runtime by delay bdev name, latency in microseconds, and `spdk_bdev_delay_io_type`. Return values distinguish missing bdev (`-ENODEV`) from invalid delay type or non-delay device (`-EINVAL`).
