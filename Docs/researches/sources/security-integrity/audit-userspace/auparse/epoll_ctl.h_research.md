# sources/security-integrity/audit-userspace/auparse/epoll_ctl.h

Purpose: Build-time table mapping `epoll_ctl(2)` operation values to names.

Important APIs, types, and functions: Defines `_S(1, "EPOLL_CTL_ADD")`, `_S(2, "EPOLL_CTL_DEL")`, and `_S(3, "EPOLL_CTL_MOD")`. `Makefile.am` generates `epoll_ctls.h` with `gen_epoll_ctls_h --i2s epoll_ctl`.

Control flow: No runtime flow.

State and persistence: Static table source and generated lookup output.

Dependencies and integration points: Values are tied to `include/uapi/linux/eventpoll.h`; auparse interpretation uses generated output for epoll control fields.

Risks and edge cases: Small stable table, but incorrect values would mislabel epoll audit events.

Test signals: Generated table build and interpretation tests for epoll operations.
