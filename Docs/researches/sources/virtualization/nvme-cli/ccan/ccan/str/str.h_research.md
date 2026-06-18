# File Research: sources/virtualization/nvme-cli/ccan/ccan/str/str.h

- Purpose: string utility macros and safer character helpers.
- Key APIs: `streq`, `strstarts`, `strends`, `stringify`, `strcount`, `STR_MAX_CHARS`, and `cis*` wrappers around ctype.
- Debug mode: under `CCAN_STR_DEBUG`, replaces libc ctype macros with checked wrappers and makes `strstr/strchr/strrchr` const-preserving with GNU `typeof`.
- Safety: `cis*` wrappers cast through `unsigned char`, avoiding common signed-char ctype misuse.
