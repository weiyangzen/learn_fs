# File Research: sources/virtualization/libguestfs/daemon/scrub.c

Wraps secure overwrite/free-space scrubbing.

Important behavior:
- Optgroup availability checks `scrub`.
- `do_scrub_device` runs `scrub <device>`.
- `do_scrub_file` resolves `sysroot_realpath(file)` and runs `scrub -r`.
- `do_scrub_freespace` sysroot-prefixes a directory and runs `scrub -X`.
- Errors include original guest path/device and command stderr.

Filesystem relevance: destructive data sanitization for devices, files, and free space.
