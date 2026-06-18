# File Research: sources/os/darwin/xnu/bsd/vfs/doc_tombstone.c

This file implements per-thread document-ID tombstone tracking used by Darwin VFS rename/delete/create flows to preserve document identity across application “safe save” patterns.

Core data model:
- Tombstone state is stored on the current `uthread` in `ut->t_tombstone`.
- The state records the prior parent vnode, parent vid, item vnode, item vid, file id, document id, and filename.
- The implementation assumes related safe-save operations happen on the same thread.

Functions:
- `doc_tombstone_get()` lazily allocates a zeroed `struct doc_tombstone` for the current thread using `kalloc_type`.
- `doc_tombstone_clear(struct doc_tombstone *ut, vnode_t *old_vpp)` clears the stored parent/name/document-id fields and, if requested, tries to return a still-valid old item vnode with an iocount.
- `doc_tombstone_should_ignore_name(const char *nameptr, int len)` filters temporary names beginning with `atmp` or ending in `.bak`/`.tmp`.
- `doc_tombstone_should_save(struct doc_tombstone *ut, struct vnode *vp, struct componentname *cnp)` refuses to save if the component name is missing, or if an existing tombstone for the same vnode would be overwritten by an ignorable temp name.
- `doc_tombstone_save(struct vnode *dvp, struct vnode *vp, struct componentname *cnp, uint64_t doc_id, ino64_t file_id)` records the parent/name and document identity for a vnode.

Important correctness details:
- Vnode identity is checked using `vnode_vid()` because stored vnode pointers may be recycled.
- `doc_tombstone_clear()` rechecks the vid after `vnode_get()` and rejects vnodes marked `VL_TERMINATE`.
- The caller remains responsible for generating corresponding fsevents.
- Temporary-file filtering exists specifically to avoid losing useful tombstone state during unusual safe-save sequences from applications.

This file is small but sits on a sensitive VFS identity-preservation path: it prevents replacement-style saves from accidentally losing document IDs when the “real” file is removed and recreated through temporary filenames.
