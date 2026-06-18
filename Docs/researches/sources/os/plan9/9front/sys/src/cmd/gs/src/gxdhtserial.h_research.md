# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtserial.h

This header declares the public interface for traditional halftone serialization and deserialization/installation.

It forward-declares `gs_memory_t`, `gx_device`, `gx_device_halftone`, and `gs_imager_state`. `gx_ht_write` serializes a `gx_device_halftone` for a given device into a caller-provided buffer, updating the size with either bytes used or bytes required. `gx_ht_read_and_install` reconstructs a halftone from serialized bytes and installs it into an imager state for a given device and allocator.

The comments document return conventions: `0` for successful write, `gs_error_rangecheck` when the buffer is too small, other errors without size mutation, and byte count or negative error for read/install.

Filesystem relevance: none directly. It is rendering command-list state serialization.
