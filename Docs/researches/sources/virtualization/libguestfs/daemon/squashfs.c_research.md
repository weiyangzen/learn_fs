# File Research: sources/virtualization/libguestfs/daemon/squashfs.c

Creates SquashFS images from guest paths and streams them out.

Important behavior:
- Optgroup availability checks `mksquashfs`.
- Converts input path to `sysroot_path`.
- Creates temporary output under `/var/tmp` rather than `/tmp` to avoid tmpfs size limits.
- Builds `mksquashfs <path> <tmpfile> -noappend -root-becomes <path> -wildcards -no-recovery`.
- Supports optional compressor and exclude list via an exclude-from file.
- Streams the resulting image over FileOut and unlinks temp files via cleanup attributes.

Filesystem relevance: packages a guest subtree into a SquashFS filesystem image.
