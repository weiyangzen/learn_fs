# File Research: sources/local-fs/xfsdump/restore/tree.h

## Summary
Declares the restore directory-tree API used by content restore code.

## Main Contents
- Initialization and resume: `tree_init()`, `tree_sync()`, `tree_check_dump_format()`.
- Root workaround: `tree_fixroot()`.
- Directory ingest: `tree_begindir()`, `tree_addent()`, `tree_enddir()`.
- Selection: `tree_markallsubtree()`, `tree_subtree_parse()`, `tree_subtree_inter()`.
- Post-processing: `tree_marknoref()`, `tree_adjref()`, `tree_post()`, `tree_delorph()`.
- Non-directory restore traversal: `tree_cb_links()`.
- Directory metadata/extattr traversal: `tree_setattr()`, `tree_extattr()`.
- Optional `tree_chk()` sanity check when `TREE_CHK` is enabled.

## Risks
The interface exposes a multi-phase protocol. Callers must initialize/sync, ingest directories, adjust references, post-process, restore files, and set attributes in the intended order.

Many functions assume the global persistent tree context exists; the header does not encode those lifecycle preconditions.
