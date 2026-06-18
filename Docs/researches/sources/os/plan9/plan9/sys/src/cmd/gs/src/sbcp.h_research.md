# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbcp.h

Interface for BCP and TBCP stream filters.

It declares encode templates `s_BCPE_template` and `s_TBCPE_template`. For decode, it defines `stream_BCPD_state` with:

- Client callbacks `signal_interrupt` and `request_status`.
- Dynamic state fields `escaped`, `matched`, `copy_count`, and `copy_ptr`.

It declares `private_st_BCPD_state`, `s_BCPD_template`, and `s_TBCPD_template`.

This is Ghostscript stream protocol state, not filesystem logic.
