# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvec.c

Implements shared utility code and default Ghostscript device procedures for high-level “vector” output devices.

Key behavior:
- Publishes GC structure descriptors for vector devices and vector image enumerators.
- Provides default `setflat`, path writing, and rectangle writing implementations for vector-device procedure tables.
- `gdev_vector_dopath` enumerates Ghostscript paths, optimizes rectangular paths through `dorect` when possible, optionally merges collinear line segments, avoids isolated `moveto` fills that trigger Acrobat Reader artifacts, and emits begin/move/line/curve/close/end callbacks.
- `gdev_vector_init` and `gdev_vector_reset` initialize cached graphics state, saved high-level fill/stroke colors, clipping IDs, scale, page state, and cached black/white colors.
- `gdev_vector_open_file_options` opens OutputFile as seekable or sequential, allocates stream buffer/stream state, optionally opens a bbox tracking device, and makes stream close flush rather than close the underlying file.
- `gdev_vector_stream` lazily calls the device `beginpage` callback on first page output.
- Updates cached logical operation, fill color, stroke color, flatness, dash, linewidth, line cap/join, and miter limit only when changed.
- `gdev_vector_stroke_scaling` computes a scalar stroke scale for uniform CTMs or a normalized matrix for anisotropic CTMs.
- Provides helpers for writing polygons, rectangles, clip paths, and clip-path updates from either path-valid clips or rectangular clip lists.
- `gdev_vector_close_file` frees bbox/stream resources and closes the underlying Ghostscript output file, reporting I/O errors.
- `gdev_vector_begin_image` initializes shared image-enumerator state, updates log-op/clip/fill color as needed, and forwards image bounds to the optional bbox device.
- `gdev_vector_end_image` can pad missing image rows, forwards image end to the bbox device, and frees the image enumerator.
- `gdev_vector_get_params`/`put_params` expose `OutputFile`, reject unsafe filename changes after output has begun, and reopen output when allowed.
- Default fill/stroke/trapezoid/parallelogram/triangle device procedures translate raster-ish operations into vector path callbacks where possible, otherwise fall back to Ghostscript defaults.

Dependencies:
- Uses Ghostscript math, memory, platform file, parameter, path, clipping, imager-state, color, stream, and bbox-device APIs.
- Implements the interface declared in `gdevvec.h`.

Research notes:
- This is a framework file: concrete vector formats supply `gx_device_vector_procs`, while this file handles state caching and common geometry conversion.
- In `gdev_vector_stroke_path`, anisotropic scaling is detected, but the default `dopath` call still passes `NULL` for the matrix, making fallback behavior important for cases requiring CTM rewriting.
