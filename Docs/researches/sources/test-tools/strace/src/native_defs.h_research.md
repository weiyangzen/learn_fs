<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/native_defs.h -->
# sources/test-tools/strace/src/native_defs.h

Purpose: maps mpers printer macro names to native printer declarations in non-mpers builds.
Important APIs/types/functions: includes `native_printer_decls.h` and defines `MPERS_PRINTER_NAME(printer_name)` as identity.
Control flow: preprocessor-only adapter. State and persistence behavior: no runtime state.
Dependencies and integration points: mpers-aware decoder compilation such as loop and mtd ioctl printers. Risks: wrong macro mapping breaks symbol names between native and compat printer builds. Test signals: native build and mpers-enabled build link checks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/native_defs.h -->
