# File Research: sources/virtualization/spdk/module/bdev/passthru/vbdev_passthru.h

This public module header declares the passthru bdev management API used by the RPC file.

`bdev_passthru_create_disk()` creates or defers creation of a passthru bdev over a named base bdev, with an optional UUID. `bdev_passthru_delete_disk()` unregisters a passthru bdev by name and reports completion through an SPDK bdev unregister callback. The header includes SPDK bdev and bdev module interfaces but exposes no implementation structs.
