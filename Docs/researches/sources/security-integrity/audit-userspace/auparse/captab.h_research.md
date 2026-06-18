# sources/security-integrity/audit-userspace/auparse/captab.h

Purpose: Build-time table mapping Linux capability numbers to lower-case capability names.

Important APIs, types, and functions: Defines `_S()` rows for capabilities 0 through 40, including newer names such as `perfmon`, `bpf`, and `checkpoint_restore`. `Makefile.am` generates `captabs.h` with `gen_captabs_h --i2s cap`.

Control flow: No runtime control flow in this file.

State and persistence: Static input to generated interpretation tables.

Dependencies and integration points: Values are tied to `include/uapi/linux/capability.h` and used by auparse interpretation of capability fields and bitmaps.

Risks and edge cases: Kernel capability additions require updates. Names are lower-case without `CAP_` prefix, so callers expecting kernel macro names need to account for auparse display format.

Test signals: Capability interpretation tests and generated table build coverage.
