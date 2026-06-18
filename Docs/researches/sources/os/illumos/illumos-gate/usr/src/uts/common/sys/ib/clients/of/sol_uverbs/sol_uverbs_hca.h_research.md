# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_hca.h

This sol_uverbs HCA-management header defines the shared HCA list and common client/event-handler API used by OFA kernel agents.

Core definitions:
- `sol_uverbs_hca_t` tracks one IBT HCA: list entries, event handler list/lock, client data list/lock, IBT client/HCA handles, GUID, HCA attributes, port count, port info pointer, and port info size.
- `sol_uverbs_ib_client_t` registers add/remove callbacks for HCA availability.
- `sol_uverbs_ib_event_handler_t` registers per-HCA async event callbacks.
- `SOL_UVERBS_INIT_IB_EVENT_HANDLER` initializes event handlers.

API surface:
- Common HCA init/fini, handle-to-HCA lookup, client register/unregister, client data get/set, event handler register/unregister, user-QP-ID to IBT handle lookup, and disabling/enabling user QP modify.

Risk-sensitive invariants:
- sol_uverbs owns the shared IBT client handle used by multiple OFA user-kernel agents.
- HCA client and event-handler lists require their matching locks.
- HCA add/remove callbacks define availability ordering for dependent OFED compatibility modules.
