## sources/security-integrity/libcap/libcap/cap_extint.c

Purpose: converts capability sets between libcap's internal `cap_t` and portable external binary representation.

Important APIs/functions: `cap_size()`, `cap_copy_ext()`, `cap_copy_int()`, `cap_copy_int_check()`, internal `_cap_size_locked()`, and `struct cap_ext_struct`.

Control flow: computes minimal byte width needed across effective/permitted/inheritable sets while preserving a historic minimum, exports magic/version length plus per-byte little-endian stacked flag data, imports by validating magic and reconstructing u32 flag blocks, and check-import validates the supplied length before delegating.

State/persistence: caller-provided buffers and newly allocated `cap_t`; no persistent state.

Dependencies/integration: internal `cap_t` layout from `libcap.h`; public binary APIs used by Go/C compatibility tests.

Risks: `cap_copy_int()` intentionally trusts the external length and can overread malformed input; callers should prefer `cap_copy_int_check()`. Export returns `EINVAL` when destination is too short rather than required size.

Test signals: `compare-cap.go` C/Go binary round trips, malformed length tests for `cap_copy_int_check`, and capsets with high-numbered bits.
