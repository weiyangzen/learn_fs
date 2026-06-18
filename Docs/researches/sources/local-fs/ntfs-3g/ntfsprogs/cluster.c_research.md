# File Research: sources/local-fs/ntfs-3g/ntfsprogs/cluster.c

Implements `cluster_find()`, a helper for locating which NTFS inode attributes own a target LCN range. It is used by ntfsprogs code such as `ntfscluster`.

The function creates an MFT search context, restricts it to in-use base records, iterates every matching inode, creates an attribute search context for each inode, enumerates attributes with `find_attribute(AT_UNUSED, ...)`, skips resident attributes, decompresses non-resident mapping pairs, and compares each real run’s LCN span against the requested `[c_begin, c_end]` range. Sparse/discontiguous pseudo-runs with negative LCNs are ignored.

For each overlapping run, the caller-provided callback receives the inode, attribute record, runlist element, and caller data. If the callback returns nonzero, `cluster_find()` exits immediately with `1`; otherwise it logs how many inodes had matches and returns `0`. On setup/decompression errors it returns `-1`.

Dependencies include MFT search helpers from `utils.h`, libntfs attribute search and mapping-pair decompression, runlist structures, and logging. A notable resource invariant is that attribute and MFT search contexts are released on normal/error exits, but early callback success returns directly from inside the loop.
