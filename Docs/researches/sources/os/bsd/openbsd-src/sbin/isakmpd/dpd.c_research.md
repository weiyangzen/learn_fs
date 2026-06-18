# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dpd.c

Implements RFC 3706 Dead Peer Detection for isakmpd phase-1 SAs. It advertises DPD with a VENDOR ID payload, detects peer support on inbound vendor payloads, handles R_U_THERE/R_U_THERE_ACK notify messages, and runs timer-driven liveness probes after phase 1 completes.

Key behavior:
- `dpd_add_vendor_payload()` allocates an ISAKMP vendor payload containing the RFC 3706 DPD vendor ID plus version bytes.
- `dpd_check_vendor_payload()` compares incoming vendor payload bodies and sets `EXCHANGE_FLAG_DPD_CAP_PEER` on the current exchange.
- `dpd_start()` enables DPD on an ISAKMP SA only when `General/DPD-check-interval` is positive.
- `dpd_handle_notify()` validates sequence numbers, replies to R_U_THERE, marks ACKs as handled, and resets the DPD timer when peer activity is confirmed.
- `dpd_event()` first checks kernel IPsec SAs for recent `last_used` activity via PF_KEY; only if no child SA traffic was recently observed does it send R_U_THERE.
- `dpd_check_event()` retries up to `DPD_RETRANS_MAX`; on failure it deletes all ready phase-2 SAs matching the phase-1 IDs and then deletes the ISAKMP SA.

Important dependencies:
- SA lifetime and lookup: `sa_find()`, `sa_delete()`, `SA_FLAG_DPD`, `SA_FLAG_READY`.
- Kernel activity: `pf_key_v2_get_kernel_sa()`.
- Timers: `timer_add_event()`, `timer_remove_event()`.
- Messages: `message_send_dpd_notify()`, payload macros from `isakmp_fld.h`.

Notable implementation detail:
- The initial DPD sequence is randomized with the MSB cleared, then incremented.
- Duplicate inbound R_U_THERE packets are tolerated until the duplicate count reaches `DPD_RETRANS_MAX`.
- `dpd_find_sa()` compares `id_i`/`id_r` using the candidate SA’s ID lengths; callers rely on matching phase-2 SAs with ready state.
