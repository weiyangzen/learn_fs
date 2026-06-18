# File Research: sources/virtualization/spdk/lib/nvmf/ctrlr_discovery.c

Read completely: yes, 332 lines.

Purpose: implements NVMe-oF discovery log generation and asynchronous Get Log Page handling for discovery controllers.

Key responsibilities:
- Maintains discovery generation changes through `spdk_nvmf_send_discovery_log_notice()`.
- Filters discovery entries by transport type, address, service ID, and optional custom filter.
- Builds a dynamic `spdk_nvmf_discovery_log_page` from active subsystems, active listeners, and target referrals.
- Completes Get Log Page asynchronously on the app thread, copying requested ranges into request iovecs and zero-filling the remainder.

Important control flow:
- `nvmf_generate_discovery_log()` iterates all target subsystems, skips inactive/deactivating subsystems, enforces host access, checks listener active state, applies discovery filters, then appends entries.
- Discovery subsystem entries set `DUPRETINFO` and `EPCSD` flags.
- Referral entries are appended after subsystem listener entries, subject to referral host allow-list checks.
- `nvmf_get_discovery_log_page_async()` snapshots host NQN, offset, length, source trid, and RAE flag, then sends work to the app thread.

Concurrency and ownership:
- Discovery log generation asserts app-thread execution.
- Async context owns duplicated `hostnqn` and is freed after request completion.
- Generated log pages are heap allocated and freed after copying.

Notable edge cases:
- Offset at or beyond generated log size returns Invalid Field.
- If allocation fails during entry growth, generation stops at the entries already accumulated.
- Custom discovery filter is only valid when target setup supplied `g_custom_discovery_filter`.

Dependencies:
- Uses target/subsystem/listener internals from `nvmf_internal.h`.
- Calls transport-specific `nvmf_transport_listener_discover()` to fill transport fields.
- Relies on `spdk_nvmf_referral_host_allowed()` from `nvmf.c`.
