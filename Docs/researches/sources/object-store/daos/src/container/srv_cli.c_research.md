# sources/object-store/daos/src/container/srv_cli.c

## Purpose
`srv_cli.c` provides server-side helpers that create, expose, and tear down client-style container handles inside a DAOS server process. This lets server code call client DAOS APIs while still populating the local `dc_cont` structures with server-fetched container properties and checksum configuration.

## Important APIs and Functions
- `dsc_cont_open(poh, cont_uuid, coh_uuid, flags, coh)` creates a `dc_cont`, initializes its properties/checksummer from server metadata, links it into the owning `dc_pool`, stores the requested container handle UUID and capabilities, and publishes a DAOS handle to the caller.
- `dsc_cont_close(poh, coh)` reverses `dsc_cont_open`: it resolves the `dc_cont` and `dc_pool`, unlinks the handle, removes the container from the pool container list, destroys the checksummer, and drops references.
- `dsc_cont_init_props(cont, pool_uuid, cont_uuid)` calls `ds_cont_get_props` to populate `cont->dc_props`, then creates `cont->dc_csummer` when the container checksum type is enabled.
- `dsc_cont2csummer(coh)` resolves a DAOS container handle and returns the container checksummer pointer.
- `dsc_cont_get_props(coh, props)` returns a copy of cached container properties from a handle.

## Control Flow
Open first respects an already valid output handle: if `*coh` resolves to an existing `dc_cont`, it returns success. Otherwise it requires a valid pool handle, allocates a new `dc_cont`, reads persistent container properties through server service APIs, configures checksum state, records flags and UUIDs, links the container into `pool->dp_co_list` under `dp_co_list_lock`, and publishes the handle through `dc_cont_hdl_link` and `dc_cont2hdl`.

Close tolerates a missing container handle by returning success. If the pool handle is missing, it returns `-DER_NO_HDL`. On success it unlinks the handle references and removes the container from the pool's list while holding the write lock.

## State and Persistence Behavior
The file does not change persistent RDB metadata. It reads container properties through `ds_cont_get_props` and mirrors them in process-local `dc_cont` state. It owns in-memory references, pool list membership, capabilities, handle UUIDs, and checksummer lifetime for server-internal use.

## Dependencies and Integration Points
This file bridges client internals (`cli_internal.h`, `dc_hdl2cont`, `dc_cont_alloc`, `dc_cont2hdl`) with server container metadata (`daos_srv/container.h`, `ds_cont_get_props`). It depends on DAOS checksum helpers (`daos_csummer_init_with_type`, `daos_contprop2hashtype`, `daos_cont_csum_prop_is_enabled`) and pool handle internals (`dc_hdl2pool`, `dp_co_list_lock`).

## Risks and Edge Cases
- `dsc_cont2csummer` returns a raw pointer after dropping the `dc_cont` reference. Callers must ensure the handle/container lifetime outlives use of the checksummer.
- `dsc_cont_open` publishes local state only; it does not perform a full metadata open RPC. Callers must already be in a context where the server-side handle UUID and permissions are valid.
- Error paths after allocation rely on final `dc_cont_put`/`dc_pool_put` cleanup. Changes must preserve reference balance around `dc_cont_hdl_link`, `dc_cont2hdl`, and list insertion.
- `dsc_cont_close` returns success for an unknown container handle, matching idempotent close behavior but potentially hiding misuse in internal callers.

## Test Signals
Server-side API tests that open/close internal container handles, checksum-enabled container tests, leak/reference-count tests, and invalid handle tests are relevant. Tests should verify pool list insertion/removal and that checksummer initialization follows container properties.
