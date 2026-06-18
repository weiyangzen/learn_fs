<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/t_chmod_secure.c -->
# sources/sync-backup/rsync/t_chmod_secure.c

Purpose: standalone C test harness for `do_chmod_at()` confinement in daemon-without-chroot mode, especially the symlink parent-component attack associated with CVE-2026-29518 follow-up hardening.

Important APIs/types/functions: `kernel_resolve_beneath_supported()`, `check()`, and `main()`. It defines rsync globals required by `syscall.c` and declares external `am_daemon`/`am_chrooted`.

Control flow: chdir to the supplied module directory, simulate `am_daemon=1` and `am_chrooted=0`, probe whether the running kernel supports resolve-beneath semantics, then run four scenarios: chmod through an in-tree directory symlink, chmod through an escaping symlink, chmod a plain relative path, and chmod a top-level file. `check()` validates return success/rejection and final mode.

State and persistence behavior: mutates modes of fixture files inside the provided test directory and verifies the outside trap file remains unchanged.

Dependencies and integration points: links with rsync syscall/object stubs, uses `openat2_usable()` when available, and expects a shell test wrapper to create `realdir`, `inside_link`, `escape_link`, `../trap`, sentinel files, and `topfile`.

Risks: expected behavior for in-tree symlinks is platform-dependent: kernels with resolve-beneath should allow them, portable fallback rejects them. The test must therefore probe runtime support instead of hardcoding one outcome. It is meaningful only when daemon/no-chroot globals are set.

Test signals: success prints OK for all scenarios and returns 0. Failures indicate either escape not rejected, legitimate path broken unexpectedly for that platform tier, or ordinary chmod regression.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/t_chmod_secure.c -->
