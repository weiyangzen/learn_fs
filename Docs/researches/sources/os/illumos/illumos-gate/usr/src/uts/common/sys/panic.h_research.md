# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/panic.h

## Purpose
Defines panic-time buffer sizing, persistent panic-data formats, summary-dump header format, kernel panic globals, and architecture/platform hooks used by the common panic path.

## Main Interfaces
- Sizes and versions:
  - `PANICSTKSIZE`
  - `PANICBUFSIZE`
  - `PANICBUFVERS`
  - `PANICNVNAMELEN`
  - `STACK_BUF_SIZE`
  - `SUMMARY_MAGIC`
- `panic_nv_t`: fixed-length name/value panic datum.
- `panic_data_t`: panic buffer header with version, message offset, image UUID, and variable name/value data.
- `summary_dump_t`: summary dump header with magic and stack-buffer checksum.
- Kernel-only panic name/value macros:
  - `PANICNVGET()`
  - `PANICNVADD()`
  - `PANICNVSET()`
- Kernel panic globals:
  - `panicbuf`
  - `panic_thread`
  - `panic_cpu`
  - `panic_hrtime`
  - `panic_hrestime`
  - `panic_bootstr`, `panic_bootfcn`, `panic_forced`, `halt_on_panic`, `nopanicdebug`, `do_polled_io`, `obpdebug`, `in_sync`, `panic_quiesce`, `panic_dump`, `panic_lbolt64`, `panic_regs`, `panic_reg`, `panic_dip`
- Platform hooks:
  - `panic_saveregs()`
  - `panic_savetrap()`
  - `panic_showtrap()`
  - `panic_stopcpus()`
  - `panic_enter_hw()`
  - `panic_quiesce_hw()`
  - `panic_dump_hw()`
  - `panic_trigger()`

## Dependencies And Relationships
Includes kernel thread, CPU, type, and DDI type headers outside assembly. Panic data is consumed by dump code and debuggers.

## Research Notes
`panic_data_t` stores the panic message and optional register-like name/value data in one fixed buffer. The `pd_msgoff` field doubles as the delimiter between structured `panic_nv_t` entries and the panic message.
