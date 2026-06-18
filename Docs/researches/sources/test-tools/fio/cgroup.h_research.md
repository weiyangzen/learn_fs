## sources/test-tools/fio/cgroup.h

Purpose: declares the cgroup integration boundary and provides no-op/error stubs when fio is built without `FIO_HAVE_CGROUPS`.

Important APIs and types: under cgroup support it defines `struct cgroup_mnt { char *path; bool cgroup2; }` and declares `cgroup_setup()`, `cgroup_shutdown()`, and `cgroup_kill()`. Without support it forward-declares `struct cgroup_mnt`, makes `cgroup_setup()` report `EINVAL` through `td_verror()`, and turns shutdown/kill into empty inline functions.

Control flow and state: the header lets callers compile a single code path regardless of cgroup availability. Runtime state is intentionally opaque outside the mount path/type pair.

Dependencies and integration: consumers need `struct thread_data` and `struct flist_head` visible from surrounding fio headers. The header is included by job lifecycle code and by `cgroup.c`.

Risks and test signals: stub behavior means unsupported builds fail only when cgroup setup is requested, not at parse time. Test coverage should include both configured and unconfigured builds to catch accidental reliance on `struct cgroup_mnt` internals.
