# File Research: sources/virtualization/spdk/module/bdev/ocf/volume.h

This private OCF header declares the volume adapter entry points implemented by `volume.c`.

It includes OCF, OCF context, and OCF data headers, then exports `vbdev_ocf_volume_init()` and `vbdev_ocf_volume_cleanup()`. The include guard name is `VBDEV_OCF_DOBJ_H`, which is broader than the file name but only protects these two declarations.
