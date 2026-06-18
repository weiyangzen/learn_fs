<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/t_stub.c -->
# sources/sync-backup/rsync/t_stub.c

Purpose: simple rsync symbol stub file that lets standalone C test helpers link against selected rsync objects without the full rsync binary.

Important APIs/types/functions: global variables for rsync modes/config (`do_fsync`, `inplace`, `am_daemon`, `am_chrooted`, `module_id`, `module_dirlen`, preservation flags, `max_alloc`, `partial_dir`, `module_dir`, `daemon_filter_list`) and stub functions `rprintf()`, `rsyserr()`, `_exit_cleanup()`, `check_filter()`, `copy_xattrs()`, `free_xattr()`, `free_acl()`, `lp_name()`, `lp_use_chroot()`, `who_am_i()`, `csum_len_for_type()`, and `canonical_checksum()`.

Control flow: logging stubs print to stderr; `_exit_cleanup()` reports the requested exit and terminates; most feature hooks return inert defaults.

State and persistence behavior: initializes process globals used by linked rsync modules. No persistent filesystem state is changed by the stubs themselves.

Dependencies and integration points: included by test executables such as secure path/chmod harnesses. It intentionally relies on `curr_dir` being defined by `syscall.c`.

Risks: stubs can mask behavior that depends on real configuration, filters, xattrs, ACLs, or checksum choices. `max_alloc` is deliberately unlimited because zero would trip rsync allocation guards in tests.

Test signals: successful linkage and predictable stderr output from helper programs are the main signals. Tests that need real filters, xattrs, ACLs, or module config should not use this stub unchanged.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/t_stub.c -->
