# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_jailmeta.c

## Purpose
Adds generic OSD-backed jail metadata parameters: private `meta` hidden from the jail and shared `env` readable by the jail.

## Main Elements
- `security.jail.meta_maxbufsize` manages hard and soft maximum metadata buffer sizes under `allprison_lock`.
- Sysctl parameter announcements expose `security.jail.param.meta` and `.env` as key/value-style jail parameters sized by the soft limit.
- `struct meta` describes each metadata namespace, its OSD slot, and OSD method table.
- Hunk-chain helpers (`jm_h_*`) edit final metadata buffers by replacing the whole buffer or cutting/replacing/removing individual `key=value` lines.
- `jm_osd_method_set()` scans jail options with the namespace prefix, validates size and NUL termination, copies existing OSD data, applies edits, assembles a final buffer, and compares/swaps under `pr_mtx` with limited retries to avoid lost concurrent updates.
- `jm_osd_method_get()` returns whole metadata or a single key value to matching vfsopts.
- `jm_osd_method_check()` marks matching options seen during jail validation.
- `jm_sysctl_env()` lets a jail read its shared `env` metadata.
- Sysinit registers two jail OSD slots with destructors and method tables; sysuninit deregisters them.

## Dependencies And Integration
Uses jail OSD methods invoked from `kern_jail.c`, vfs option parsing, jail locks, `allprison_lock`, sysctl jail parameter discovery, and `M_PRISON` storage.

## Risk Notes
The buffer editing logic is compact but subtle. It treats metadata as newline-separated `key=value` strings, depends on vfsopt NUL-terminated values, and uses hunk slicing to avoid in-place mutation of shared OSD buffers. The get path’s single-key extraction assumes newline-delimited records; malformed metadata could affect lookup boundaries, though set-side validation and assembly constrain normal data.
