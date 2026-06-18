# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl.h

## Purpose

`impl/ibtl.h` is the main private implementation header for IBTL. It defines the internal object graph, async/CQ state, resource accounting, macros for converting IBTL handles to CI objects, and private IBTL initialization/synchronization entry points.

## Main Structures

`ibtl_clnt_t` tracks a registered client, its module info, private pointer, devinfo, service count, HCA list, and subnet notice handler. `ibtl_hca_devinfo_t` represents a CI-registered HCA device with state, portinfo cache, client list, CI handle and ops vector, HCA attributes, devinfo, async state, port async data, FMA data, MultiSM flag, and kstat metadata.

`ibtl_hca_t` is a client’s open HCA handle and tracks links, client/device pointers, closing flag, resource counters for QPs/EECs/CQs/PDs/AHs/MRs/MWs/QPNs/SRQs/FMR pools, and async accounting.

`ibtl_cq_t`, `ibtl_srq_t`, `ibtl_qp_t`, `ibtl_eec_t`, and `ibtl_channel_t` represent internal CQ, SRQ, QP, EEC, and channel objects. Channels embed `ibtl_qp_t` first and add transport-specific RC/RD/UD state, current CEP state, client private data, CM private data, mutex, and condition variable.

## Synchronization and Macros

The header defines async pending/free flags, CQ pending/call-client/free flags, RC QP connection/free-state flags, and `_NOTE` annotations for lock and data-access expectations. Macros convert between channels, QPs, CI HCA handles, CI operation vectors, client handles, module info, HCA GUIDs, port counts, and table sizes.

## Functions and Globals

Private prototypes cover HCA lookup, portinfo init/reinit, CEP state/time/logging/thread initialization and teardown, new-HCA announcement, client detach, QP flow control, async free checks, CQ free synchronization, and HCA close synchronization. Globals include the HCA list, client list/mutex, free-QP mutex, close-HCA condition variable, QP flow-control mutex/CV, well-known async handlers for CM/DM/IBMA, and a fast GID cache validity flag.

## Research Notes

This header is the internal map for IBTL lifetime management. The resource counters and async-free flags are important for detach and free races, especially for storage clients that may hold CQs, channels, and registered memory while asynchronous errors are being delivered.
