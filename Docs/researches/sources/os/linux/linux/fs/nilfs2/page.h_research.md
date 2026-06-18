# File Research: sources/os/linux/linux/fs/nilfs2/page.h

`page.h` declares NILFS buffer/folio helpers and defines NILFS-specific buffer-head state bits starting at `BH_PrivateStart`: allocated, node, volatile, checked, and redirected. Generated `BUFFER_FNS` helpers expose node, volatile, checked, and redirected predicates/setters.

The declared API covers buffer acquisition, forgetting, copying, clean-buffer checks, dirty-page copying between mappings, shadow-copy restoration, dirty-page clearing, counting clean buffers over a folio byte range, and finding uncommitted delayed extents.

`NILFS_FOLIO_BUG()` prints detailed folio/buffer diagnostics via `nilfs_folio_bug()` and then triggers `BUG()`. This is used when NILFS detects impossible page-cache state during metadata/data copying.
