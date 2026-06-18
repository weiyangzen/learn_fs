# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client_impl.h

## Role

Private implementation layout for MAC clients, unicast entries, promiscuous callbacks, per-CPU Tx references, VLAN validation/cache, protection state, and internal client helper APIs.

## Structure

- Declares kmem caches and defines `mac_unicast_impl_t`, `mac_promisc_impl_t`, `mac_tx_percpu_t`, client role flags, and client implementation state flags.
- Defines `mac_client_impl_t` with client identity, associated MACs, flow entries, RX callbacks, promiscuous/unicast lists, resource callbacks, Tx notify callbacks, stats, subflows, priorities, HIO share, multicast, protection AVL trees, Tx quiesce state, and variable-size per-CPU Tx refs.
- Provides size/accessor macros, resource property accessors, VID validation/tagging helpers, single-entry VID cache encoding macros, protection flags, and internal function prototypes.

## Dependencies And Consumers

Includes modhash, public/private MAC provider headers, MAC implementation, MAC stats, network interface, and MAC flow implementation headers. Consumers are MAC client internals, not general MAC clients.

## Important Details

The comments annotate locking discipline (`WO`, `SL`, specific locks, RX quiescence). The variable-length `mci_tx_pcpu[1]` must remain last and is sized by `MAC_CLIENT_IMPL_SIZE`. `MAC_VID_CHECK()` is a statement macro that inspects Ethernet/VLAN headers directly.

## Research Notes

Read completely: 436 lines, 13945 bytes.
