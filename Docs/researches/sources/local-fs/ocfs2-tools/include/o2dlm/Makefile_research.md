# File Research: sources/local-fs/ocfs2-tools/include/o2dlm/Makefile

This Makefile prepares and installs public `o2dlm` headers.

Key content:
- Generates `o2dlm_err.h` by copying from `libo2dlm`, building it there if missing.
- Installs `o2dlm.h` plus generated error header under `o2dlm`.
- Cleans generated `o2dlm_err.h`.

Integration notes:
- Mirrors the generated-error-header pattern used by the `o2cb` include Makefile.
