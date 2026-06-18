# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_help.c

Help text and pager-backed help renderer for `unsquashfs` and `sqfscat`.

Key contents:
- Option-name, option-argument, section-name, and full text arrays for both programs.
- Full documented sections for extraction, information/listing, xattrs, runtime, help, miscellaneous options, environment variables, exit codes, extra documentation links, and available decompressors.
- Generic helpers to print all help, print option matches by regex, print section names, print exact/regex section matches, report invalid options, and print option-specific parse errors.
- Public wrappers: `unsquashfs_help_all()`, `unsquashfs_section()`, `unsquashfs_option()`, `unsquashfs_help()`, `unsquashfs_invalid_option()`, `unsquashfs_option_help()`, and matching `sqfscat_*` functions.
- `display_compressors()` writes the compiled decompressor list.

Dependencies:
- `print_pager.h` for `launch_pager()`, `delete_pager()`, `autowrap_print()`, and column sizing.
- `compressor.h` for `DECOMPRESSORS`.
- `unsquashfs_help.h` xattr default strings so help reflects build-time xattr support.
