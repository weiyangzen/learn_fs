# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxidata.c

Purpose: implements generic ImageType 1 image enumeration, row unpacking/repacking, rendering dispatch, flushing, and cleanup.

Main flow:
- `gx_image1_plane_data` processes incoming image planes row by row.
- Computes row byte counts, handles resumed partial progress, sets up clipping/ROP forwarding devices, unpacks or repacks source data, updates DDA row/pixel state, applies clipping checks, and invokes the selected render procedure.
- `gx_image1_flush` invokes the renderer with `h == 0` to flush buffered image data at end-of-input.
- `gx_image1_end_image` optionally flushes, releases scaler state, and frees image buffers/devices/enumerator.

Bit-planar support:
- `repack_bit_planes` combines 1 to 8 individual bit planes into byte-wide samples.
- Handles null planes by substituting zero buffers.
- Supports nonzero `data_x`, direct identity output, and lookup-table mapped output.

Device setup:
- `setup_image_device` wraps the target with clip and ROP forwarding devices when present.

State/error behavior:
- `penum->used.x/y` track partially consumed pixels/rows after render errors.
- DDA row/strip state is restored on interrupted rendering so callers can resume.
- Caller remains responsible for ending the image after normal or error returns.

Research notes:
- This is the central glue between image decoders/unpackers and specialized renderers in the other `gxi*` files.
