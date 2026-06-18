# sources/security-integrity/audit-userspace/lib/uringop_table.h

Purpose: maps auditable io_uring operation numbers to operation names. It deliberately includes only io_uring ops considered auditable and points maintainers at kernel `io_uring/opdef.c` audit-skip metadata.

Important APIs/types: feeds generated `uringop_s2i` and `uringop_i2s`, surfaced by `audit_name_to_uringop`, `audit_uringop_to_name`, and auditctl's io_uring rule listing.

Control flow: static table expansion. Missing operation numbers are intentional when kernel marks them non-auditable or they are not listed.

State and persistence: none.

Dependencies and integration: compiled under `WITH_IO_URING`; `auditctl-listing.c` prints io_uring masks via `audit_uringop_to_name`.

Risks and test signals: stale auditability decisions cause rules to reject valid operations or list numbers instead of names. `lookup_test.c` validates table round-trip when io_uring support is enabled.
