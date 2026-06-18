# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/pf_key_v2.h

This header exports the PF_KEY v2 interface used by the rest of isakmpd.

Key declarations:
- Global `pf_key_v2_socket`.
- Kernel SA lifecycle operations: `pf_key_v2_get_spi`, `pf_key_v2_set_spi`, `pf_key_v2_enable_sa`, `pf_key_v2_disable_sa`, `pf_key_v2_delete_spi`, `pf_key_v2_group_spis`.
- Kernel query: `pf_key_v2_get_kernel_sa`.
- Event handling: `pf_key_v2_open`, `pf_key_v2_handler`.
- On-demand connection hook: `pf_key_v2_connection_check`.
- Legacy/manual helper: `pf_key_v2_enable_spi`.

Integration:
- Forward declares `struct proto`, `struct sa`, `struct sockaddr`, and `struct kernel_sa`.
- Public API is consumed by DOI/IPsec code to allocate SPIs and install/delete negotiated SAs.
