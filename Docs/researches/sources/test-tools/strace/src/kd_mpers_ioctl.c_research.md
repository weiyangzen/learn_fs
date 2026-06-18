# sources/test-tools/strace/src/kd_mpers_ioctl.c

Purpose: decodes personality-dependent VT ioctl commands whose structures contain tracee-sized pointers.

Important APIs/types/functions: `MPERS_PRINTER_DECL(kd_mpers_ioctl)`, `kd_unimap`, `kd_fontx`, `kd_font_op`, `print_unipair_array_member`, `print_consolefontdesc`, `print_console_font_op`, mpers types `struct_unimapdesc`, `struct_consolefontdesc`, `struct_console_font`, and `struct_console_font_op`.

Control flow: the mpers dispatcher handles `GIO_UNIMAP`/`PIO_UNIMAP`, `GIO_FONTX`/`PIO_FONTX`, and `KDFONTOP`. `kd_unimap` prints entry count and decodes entries on set or successful get, preserving original count across phases. `kd_fontx` decodes console font descriptor and either pointer or glyph bytes. `kd_font_op` decodes operation-specific fields and chooses whether to continue to exit based on operation direction.

State and persistence behavior: `kd_unimap` stores `entry_ct` in `tcb` private storage; exit can report changed count and use the original count for returned arrays. No durable global state.

Dependencies and integration points: called by `kd_ioctl.c` fallback. Depends on mpers-generated layouts, KD font operation xlat tables, and tracee string/array printers.

Risks: pointer-sized fields must match tracee personality; using host structures would misdecode compat processes. `KDFONTOP` has operation-specific data semantics, including bounded font-name and glyph buffers.

Test signals: cover get/set unimap, ENOMEM behavior, changed entry counts, `GIO_FONTX` vs `PIO_FONTX`, `KD_FONT_OP_GET`, `SET`, `SET_DEFAULT`, `COPY`, unknown font ops, and compat pointer widths.
