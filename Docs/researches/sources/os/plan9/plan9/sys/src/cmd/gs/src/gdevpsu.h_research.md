# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsu.h

This header declares the shared PostScript-writing utility interface used by bitmap and vector PostScript output devices.

Main type:
- `gx_device_pswrite_common_t` stores `LanguageLevel`, `ProduceEPS`, `ProcSet_version`, and `bbox_position`.
- `PSWRITE_COMMON_PROCSET_VERSION` and `PSWRITE_COMMON_VALUES` provide consistent initializer support.

Declared APIs:
- `psw_print_lines`
- `psw_begin_file_header`
- `psw_end_file_header`
- `psw_end_file`
- `psw_write_page_header`
- `psw_write_page_trailer`

The header documents an important split between `FILE *` and Ghostscript `stream *`: some trailer/finalization operations must work after stream state is unavailable, so the API intentionally keeps file-level operations on `FILE *`.
