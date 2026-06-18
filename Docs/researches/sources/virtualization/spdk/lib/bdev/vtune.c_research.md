# File Research: sources/virtualization/spdk/lib/bdev/vtune.c

`vtune.c` conditionally includes Intel VTune static instrumentation support when `SPDK_CONFIG_VTUNE` is enabled.

It includes `spdk/config.h`, guards the rest of the file with `#if SPDK_CONFIG_VTUNE`, suppresses selected GCC warnings triggered by VTune code, and includes `ittnotify_static.c`.

Research notes: this is an integration wrapper rather than SPDK logic. Build behavior depends entirely on `CONFIG_VTUNE`.
