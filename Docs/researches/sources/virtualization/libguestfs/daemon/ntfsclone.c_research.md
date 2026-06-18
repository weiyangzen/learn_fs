# File Research: sources/virtualization/libguestfs/daemon/ntfsclone.c

Streams NTFS clone images in and out.

Important behavior:
- `do_ntfsclone_in` receives FileIn data and pipes it to `ntfsclone -O <device> --restore-image -`.
- Uses a temp stderr file so command errors can be reported after pipe failure.
- Handles receive cancellation separately from write errors.
- `do_ntfsclone_out` constructs `ntfsclone -o - --save-image` with optional metadata/rescue/ignore-fs-check/preserve-timestamps/force flags.
- FileOut streaming sends reply first, then chunks stdout, with cancellation on read or process failure.

Filesystem relevance: efficient NTFS image backup/restore over the daemon file-transfer protocol.
