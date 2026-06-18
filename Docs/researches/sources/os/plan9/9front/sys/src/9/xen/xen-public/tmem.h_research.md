# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/tmem.h

Purpose: Xen public Transcendent Memory ABI header. It defines commands and payloads for tmem pools and page/object operations.

Key interfaces:
- Commands: `TMEM_CONTROL`, `TMEM_NEW_POOL`, `TMEM_PUT_PAGE`, `TMEM_GET_PAGE`, `TMEM_FLUSH_PAGE`, `TMEM_READ`, `TMEM_WRITE`, `TMEM_XCHG`.
- Privileged commands: `TMEM_AUTH`, `TMEM_RESTORE_NEW`.
- Control subops for freeze/thaw/flush/destroy/list/save/restore.
- `tmem_op` with `creat`, `ctrl`, and generic `gen` union arms; `tmem_handle`.

Integration notes: Depends on `xen.h`; guarded for non-assembly C definitions.

Risk/attention points: Special errno values `EFROZEN` and `EEMPTY` are ABI-level values and may collide with local errno assumptions if not handled distinctly.
