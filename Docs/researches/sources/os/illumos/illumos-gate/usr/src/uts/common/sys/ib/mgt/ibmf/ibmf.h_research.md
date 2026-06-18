# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf.h

## Scope

Public IBMF client interface for registering InfiniBand management clients, sending/receiving MADs or UD traffic, managing asynchronous callbacks, allocating messages, and allocating/modifying/freeing alternate QPs.

## Public Types And Constants

- Defines IBMF status codes from `IBMF_SUCCESS` through transport, timeout, validation, callback, and transaction-ID errors.
- `IBMF_VERSION` is 1.
- `ibmf_handle_t` and `ibmf_qp_handle_t` are opaque handles; `IBMF_QP_HANDLE_DEFAULT` is the default special QP handle.
- `ibmf_client_type_t` enumerates management class/client role combinations: subnet agent/manager, SA, performance, baseboard, device, communication, SNMP, vendor ranges, application ranges, and universal class.
- `ibmf_retrans_t` defines retries, response time, round-trip time, and transaction timeout parameters.
- `ibmf_register_info_t` identifies HCA/port and client class.
- `ibmf_impl_caps_t` advertises whether default and non-default QP handles support arbitrary P_Key/Q_Key use.
- `ibmf_async_event_t` currently defines `IBMF_CI_OFFLINE`.
- `ibmf_async_event_cb_t` and `ibmf_msg_cb_t` define asynchronous interface and message callbacks.

## Main APIs

- `ibmf_register()` registers one management class on one port, with RMPP/offload flags and an async event callback.
- `ibmf_unregister()` unregisters a client and invalidates the handle.
- `ibmf_setup_async_cb()` installs an unsolicited receive callback for a handle/QP pair.
- `ibmf_tear_down_async_cb()` removes that callback.
- `ibmf_msg_transport()` sends a message synchronously or asynchronously, optionally sequenced and/or RMPP.
- `ibmf_alloc_msg()` and `ibmf_free_msg()` allocate and release IBMF message contexts.
- `ibmf_alloc_qp()`, `ibmf_query_qp()`, `ibmf_modify_qp()`, and `ibmf_free_qp()` manage alternate QPs.

## Behavioral Contracts

- Clients must register before sending or receiving management packets.
- A class can generally be registered once per port, except `UNIVERSAL_CLASS`, which permits multiple clients and should use alternate QPs only.
- Clients whose classes include an RMPP header must register with `IBMF_REG_FLAG_RMPP`.
- Callbacks may be invoked before setup/register/transport calls return; clients must tolerate early callback ordering.
- Message receive buffers supplied by IBMF must be freed with `ibmf_free_msg()`.
- Reusing receive buffers for send is only allowed for non-sequenced operations; sequenced reuse returns `IBMF_REQ_INVALID`.
- Default QP usage is constrained by registered MAD class and implementation P_Key/Q_Key capabilities.

## Flags

- Registration flags: `IBMF_REG_FLAG_RMPP`, `IBMF_REG_FLAG_NO_OFFLOAD`, `IBMF_REG_FLAG_SINGLE_OFFLOAD`.
- Transport flags: `IBMF_MSG_TRANS_FLAG_RMPP`, `IBMF_MSG_TRANS_FLAG_SEQ`.
- Alternate QP allocation flags: `IBMF_ALT_QP_MAD_NO_RMPP`, `IBMF_ALT_QP_MAD_RMPP`, `IBMF_ALT_QP_RAW_ONLY`.

## Dependencies

- Includes IB types, packet headers, common MAD definitions, IBMF message structures, SAA API, and utilities.
- Public API is used by CM, DM, DMA, SAA, and management agents/managers.

## Risks And Invariants

- `ibmf_unregister()` fails with `IBMF_BUSY` while messages, callbacks, or QPs remain active.
- Callback functions are expected not to block in unsolicited message callbacks, though IBMF does not enforce it.
- Alternate QP P_Key/Q_Key may be modified concurrently by another thread, so query/transport validation can race with caller behavior.
- Buffer ownership is split: clients own send buffers; IBMF owns receive buffers.
- Raw UD traffic has separate size and buffer-layout requirements from MAD traffic.
