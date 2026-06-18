# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstat30.c

Read completely: 57 lines.

This implements old `__fhstat30` by aliasing it to `__compat___fhstat30`. It converts the old fixed-size file-handle API by calling `__compat___fhstat40(fhp, FHANDLE30_SIZE, sb)`.

Important interactions: bridges old `compat_30_fhandle` callers to the newer length-explicit file-handle stat wrapper.

Security/reliability notes: no local validation beyond forcing `FHANDLE30_SIZE`; errors come from the downstream call.
