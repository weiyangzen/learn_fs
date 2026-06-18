<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/Utility/libkqueue.h -->
# sources/sync-backup/git-annex/Utility/libkqueue.h

Purpose: public C header for the small kqueue helper library in `libkqueue.c`.

Important APIs and types: declares `int init_kqueue();`, `void addfds_kqueue(const int kq, const int fdcnt, const int *fdlist);`, and `signed int waitchange_kqueue(const int kq);`. No structs, enums, or macros are exported, keeping the ABI intentionally narrow.

Control flow and state: this header describes a create/register/wait lifecycle. It exposes the kqueue file descriptor as an integer and leaves descriptor ownership and cleanup to callers.

Dependencies and integration points: no includes are present, so consumers do not get system declarations from this header. It is intended for local compilation with `libkqueue.c` and FFI consumers that only need function signatures.

Risks: the prototypes use old-style empty parameter lists for `init_kqueue()` rather than `void`, which is tolerated by C but less strict. There is no declaration for closing the kqueue or reporting detailed errors.

Test signals: compile tests should include the header from C and any FFI binding, link with `libkqueue.c`, and validate that the declared ABI matches the implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/Utility/libkqueue.h -->
