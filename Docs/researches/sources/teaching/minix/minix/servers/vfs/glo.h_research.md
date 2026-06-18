# File Research: sources/teaching/minix/minix/servers/vfs/glo.h

Header declaring VFS global variables and convenience macros.

Key globals:
- `fp`: current caller process.
- `susp_count`, `nr_locks`, `reviving`, `sending`, `verbose`.
- `ROOT_DEV`, `ROOT_FS_E`, `system_hz`.
- `m_in`: current input message.
- `self`: current worker thread.
- `deadlock_resolving`, `bsf_lock`, worker array, `mount_label`.
- `err_code`.
- `call_vec`.

Important macros:
- `who_p`, `who_e`, `call_nr`
- `job_m_in`, `job_m_out`, `job_call_nr`
- `fproc_addr`
- `super_user`

`EXTERN` is controlled by `_TABLE`, allowing the same header to declare or define globals.
