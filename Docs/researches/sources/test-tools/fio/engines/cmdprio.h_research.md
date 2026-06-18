# sources/test-tools/fio/engines/cmdprio.h

Purpose: Declares command-priority structures, option macros, and helper APIs shared by IO engines.

Important APIs/types: Defines `CMDPRIO_RWDIR_CNT`, mode enum, `cmdprio_prio`, `cmdprio_bsprio`, `cmdprio_bsprio_desc`, `cmdprio_options`, and `cmdprio`. The `CMDPRIO_OPTIONS(opt_struct, opt_group)` macro expands fio option table entries when `FIO_HAVE_IOPRIO_CLASS` is available, or unsupported option stubs otherwise.

Control flow: Engine option structs embed `cmdprio_options`; their option tables include `CMDPRIO_OPTIONS`; engine init calls `fio_cmdprio_init()`; queue paths call `fio_cmdprio_set_ioprio()`; cleanup calls `fio_cmdprio_cleanup()`.

State/persistence: Runtime descriptors are held in `struct cmdprio`; user options are in the engine-specific option struct.

Dependencies/integration: Includes `../fio.h` and `../optgroup.h`, and relies on fio option offsets, priority constants, and `struct io_u`.

Risks: The macro assumes the embedding option struct has a member named `cmdprio_options`. Unsupported builds still expose option names but mark them unsupported. Only read/write directions are represented.

Test signals: Compile engines with and without `FIO_HAVE_IOPRIO_CLASS`; parse all option names; verify unsupported builds reject use clearly.
