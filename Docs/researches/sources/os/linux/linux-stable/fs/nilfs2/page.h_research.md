# File Research: sources/os/linux/linux-stable/fs/nilfs2/page.h

`page.h` declares NILFS buffer/folio helper APIs and extended buffer-head state bits. Custom bits start at `BH_PrivateStart`: allocated, NILFS node, volatile, checked, and redirected. It creates buffer flag helpers for node, volatile, checked, and redirected states.

The exported functions cover buffer acquisition and disposal (`nilfs_grab_buffer`, `nilfs_forget_buffer`), buffer copying, folio cleanliness checks, diagnostic bug output, dirty-page copying and copy-back, dirty-state clearing, clean-buffer counting in a byte range, and delayed/uncommitted extent scanning.

The `NILFS_FOLIO_BUG` macro prints detailed folio/buffer diagnostics via `nilfs_folio_bug()` and then triggers `BUG()`. This header is consumed by metadata, btree node, inode, segment, and recovery code that needs NILFS-specific buffer state handling.
