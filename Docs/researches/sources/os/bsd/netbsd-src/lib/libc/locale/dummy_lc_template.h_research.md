# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/dummy_lc_template.h

Read completely: 54 lines.

This template implements a simple `setlocale` function for categories that do not load external locale data. It resolves an empty name through environment variables, accepts only `C` or `POSIX`, updates the locale's `part_name`, and returns the active category name.

Important interactions: instantiated by `dummy_lc_collate.c`. It includes `generic_lc_template_decl.h` for the generated prototype form.

Security/reliability notes: rejects arbitrary locale names for dummy categories. It stores pointers to stable string literals rather than allocating new category data.
