# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_impl.h

## Scope

Private IBMF implementation header defining internal QP, message, client, channel interface, WQE, UD destination, RMPP, taskq, kstat, state, and helper function contracts.

## Core Structures

- `ibmf_wqe_mgt_t` tracks WQE memory allocation, registered IB memory, lkey, MR handle, and mutex.
- `ibmf_qp_t` tracks special QPs: IBT QP handle, port/QP number, reference count, flags, posted receive WQEs, and mutex.
- `ibmf_alt_qp_t` tracks alternate QPs: IBT QP, sizes, owning client, receive callback, teardown CV, state flags, active send/receive counters, QPN, P_Key/Q_Key, port, RMPP support, SQD CV, WQE counts, WQE caches, vmem arena, and WQE management list.
- `ibmf_msg_impl_t` extends public `ibmf_msg_t` with list links, client/QP/UD destination, callback, TID, management class, mutex, state flags, RMPP context, retransmission data, timeout IDs, refcount, unsolicited flag, and pending send completions.
- `ibmf_client_t` tracks a registered client, taskqs, message lists, async event callback, unsolicited receive callback, client class info, special QP, CI handle, flags, registration flags, stats, base LID, and kstat pointer.
- `ibmf_send_wqe_t` and `ibmf_recv_wqe_t` wrap IBT send/receive work requests with memory registration, QP, port, message, status, and RMPP segment metadata.
- `ibmf_ci_t` represents one channel interface/HCA context with clients, QPs, CQs, PD, UD dest pool, WQE caches, HCA identity, refcount/state, wait CVs, WQE cleanup coordination, and port kstats.
- `ibmf_state_t` is global IBMF state: CI list, IBT handle, CQ handler, global mutex, module info, and fallback taskq.

## Macros And State Flags

- Defines queue sizes, WQE memory size, management Q_Key, default P_Key values, P_Key masks, and taskq sizing.
- Work request IDs mark receive completions with bit 0.
- Message flags track queued/done/blocking, sequenced, send/receive RMPP, busy/free/on-list, and termination.
- Transaction flags track uninitialized/init/wait/done/signaled/timeout/recv/send completion states.
- Client flags track active receive/send callbacks and callback teardown.
- CI flags and states track initialization, validation, invalidation, uninitialization, present/inited/gone states, and waiters.
- Callback setup/cleanup macros update active callback counts and kstats and signal teardown CVs when active callbacks drain.

## Internal APIs

- CI validation/acquire/release, client allocation/add/delete/lookup, QP allocation/query/modify/free and P_Key mapping.
- Packet send, UD destination allocation/free/pooling, WQE allocation/free/posting, completion handling, loopback detection, status conversion.
- Message initialization, client message list management, allocation/free, transport, refcount decrement, send/receive completion, and error receive-buffer setup.
- Transaction termination, client notification, sequence notification, timer set/unset/timeout callbacks.
- RMPP detection, message lookup, RMPP receive handling, RMPP send/window/termination setup.
- Alternate QP WQE cache constructors/destructors and WQE-cache extension.
- Receive callback setup/cleanup and UD destination population task dispatch.

## Dependencies

- Includes kernel module/DDI/taskq/synchronization headers, IBT verbs transport, public IBMF, RMPP, kstat, and trace headers.
- Uses IBT CQs, QPs, PDs, memory registration, UD destinations, work completions, and async HCA events.

## Risks And Invariants

- `im_mutex` protects transaction state, receive buffers, status, flags, and RMPP context.
- Client message lists are separately protected by `ic_msg_mutex`; callback and allocation state by `ic_mutex`.
- CI state and client/QP lists have distinct locks and CVs; teardown must drain active callbacks, WQEs, messages, QPs, and references in order.
- UD destination pool high/low watermarks are tuned to avoid long refill stalls while preserving stress capacity.
- WQE memory is registered with IBT and tracked by both kernel virtual allocation and IB virtual memory arenas; leaks or premature free would corrupt transport operations.
- RMPP message matching must use TID, class, method, LID/GID, and RMPP header state to distinguish transactions.
