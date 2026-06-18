# File Research: sources/windows/dokany/dokan_fuse/include/fuse_opt.h

Public FUSE option parsing API.

Key contents:
- Defines `struct fuse_opt` templates with offset/value actions.
- Defines `FUSE_OPT_KEY`, `FUSE_OPT_END`, and `struct fuse_args`.
- Defines option processing keys:
  - `FUSE_OPT_KEY_OPT`
  - `FUSE_OPT_KEY_NONOPT`
  - `FUSE_OPT_KEY_KEEP`
  - `FUSE_OPT_KEY_DISCARD`
- Declares `fuse_opt_parse`, argument insertion/add/free helpers, option list helper, and matcher.
- Uses `_strdup` on MSVC and `strdup` elsewhere via `STRDUP`.

Role:
- Lets callers and the Dokan FUSE layer parse libfuse-style command-line and `-o` option groups.
