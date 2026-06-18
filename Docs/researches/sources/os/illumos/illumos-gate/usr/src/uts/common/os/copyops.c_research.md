# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/copyops.c

This small file provides compatibility/default wrappers for physical I/O and per-thread copy operation hooks.

Core behavior:
- `physio()` delegates directly to `default_physio()`.
- `install_copyops()` asserts the target thread has no copyops installed and sets `t_copyops`.
- `remove_copyops()` asserts copyops are installed and clears `t_copyops`.
- `copyops_installed()` returns whether a thread currently has copyops.

Important invariants:
- Copyops installation is single-owner per thread; assertions catch double-install and remove-without-install misuse.
- The file does not manage copyops object lifetime; callers own the referenced `copyops_t`.
