# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa.h

## Scope

Public IBMF Subnet Administration Access (SAA) interface for opening SA sessions, issuing SA queries/updates/deletes, subscribing to subnet events, and using helper query functions.

## Public Types

- `IBMF_SAA_PKEY_WC` and `IBMF_SAA_MTU_WC` are wildcard values for P_Key and MTU.
- `ibmf_saa_access_type_t` selects retrieve, update, or delete.
- `ibmf_saa_handle_t` is an opaque SAA session handle.
- `ibmf_saa_cb_t` is the asynchronous SA access callback, returning length, host-endian unpacked result, and IBMF status.
- `ibmf_saa_access_args_t` contains SA attribute ID, access type, component mask, template pointer/length, callback, and callback arg.
- `ibmf_saa_subnet_event_t` enumerates GID available/unavailable, multicast group create/delete, capability mask change, system image GUID change, and subscription status change.
- `ibmf_saa_event_details_t` carries event-specific GID, system image GUID, capability mask, LID, or producer status mask.
- `ibmf_saa_subnet_event_cb_t` and `ibmf_saa_subnet_event_args_t` define event callback registration.

## Main APIs

- `ibmf_sa_session_open()` registers an SAA consumer on a port GUID, optionally with subnet event subscription and SM key.
- `ibmf_sa_session_close()` unregisters a consumer and cancels outstanding callbacks before returning.
- `ibmf_sa_access()` performs generic SA retrieve/update/delete operations, synchronously if no callback is supplied.
- Helpers:
  - `ibmf_saa_gid_to_pathrecords()`
  - `ibmf_saa_paths_from_gid()`
  - `ibmf_saa_name_to_service_record()`
  - `ibmf_saa_id_to_service_record()`
  - `ibmf_saa_update_service_record()`

## Event Behavior

- SAA subscribes with the SA for CA, switch, router, and subnet-management trap producer types.
- Subscription failures are reported as `IBMF_SAA_EVENT_SUBSCRIBER_STATUS_CHG` with a producer status mask.
- Event callbacks may occur before `ibmf_sa_session_open()` returns.
- Event callbacks are dispatched on separate threads, may be out of order, and may not be generated under heavy load.

## Dependencies

- Includes IB types and SA record definitions.
- Returns unpacked, host-endian SA record structures from `sa_recs.h`.

## Risks And Invariants

- Successful query results allocate buffers that the consumer must free.
- `ibmf_sa_access()` returns zero length on failure or no records.
- Callback ordering is intentionally weak; consumers must not infer strict event order.
- Session close must synchronize with outstanding asynchronous callbacks before invalidating the handle.
- Unknown SA attributes require caller-provided wire-format template length because SAA cannot pack unknown records.
