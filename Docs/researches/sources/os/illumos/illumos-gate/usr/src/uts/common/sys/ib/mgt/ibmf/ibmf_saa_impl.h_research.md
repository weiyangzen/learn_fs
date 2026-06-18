# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa_impl.h

## Scope

Private SAA implementation header defining per-port/client state, kstats, transaction context, event taskq arguments, constants, and implementation function prototypes.

## Structures And State

- Constants define max clients per port, MAD base/class versions, retry/time limits, busy retry count, and wait times.
- `saa_port_state_t` tracks registering, ready, invalid, and purging port states.
- `saa_port_t` stores list linkage, mutex/CV, state/reference count, port GUID, IBMF registration info/handle/caps/QP, timeout/class capability data, IBMF address/global address/message flags, redirect state, retransmission settings, current TID, outstanding transaction count, kstats, event-subscription masks/client list, node GUID/port number, and latest SA uptime.
- `ibmf_saa_kstat_t` tracks clients registered, failed registrations, outstanding/total/failed/timed-out requests.
- `saa_client_state_t` tracks active, waiting, and closed clients.
- `saa_client_data_t` stores handle signature, port pointer, mutex, pending transaction count, state CV/state, SM key, active event callback count/CV, and event callback info.
- `saa_state_t` stores global port list, lock, and event taskq.
- `saa_impl_trans_info_t` groups all fields for an SA transaction: client/port, request attribute/mask/template/method, async callback, sync result storage, InformInfo subscription metadata, unsubscribe sequencing, saved transport flags, busy retry count, and send time.
- `ibmf_saa_event_taskq_args_t` packages event callback dispatch.

## Functions

- Init/fini/purge and validation: `ibmf_saa_impl_init()`, `ibmf_saa_impl_fini()`, `ibmf_saa_is_valid()`, `ibmf_saa_impl_purge()`.
- Port/client setup: add client, create port, init kstats, mark registration failed, register port, get ClassPortInfo.
- Transaction send: `ibmf_saa_impl_send_request()` and `ibmf_saa_async_cb()`.
- Event subscription and notification: add subscriber, subscribe/unsubscribe events, subscribe SM events, notify clients, and `ibmf_saa_report_cb()` for report handling.

## Dependencies

- Includes public SAA API and IBMF private implementation.
- Uses IBMF handles/QPs/retransmission, kstats, taskqs, mutexes/CVs, and MAD notice structures.

## Risks And Invariants

- `saa_pt_mutex` protects port reference count, retransmission/address/redirect/TID/outstanding state.
- Registration synchronization allows only one client to perform IBMF registration for a shared port.
- Event subscription masks track arrivals and successes per producer type; status-change events depend on comparing masks over time.
- `saa_impl_trans_info_t` lifetime differs between sync and async transactions: sync freed by `ibmf_access_sa()`, async by the IBMF transport callback.
- Busy SA responses are retried with a bounded counter and sleep interval.
