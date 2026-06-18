# sources/object-store/daos/src/container/cli_internal.h

Purpose: private client-side declarations shared inside DAOS container client code.

Important APIs/types/functions: `dc_cont_hdl_link`, `dc_cont_hdl_unlink`, `dc_cont_alloc`, and `dc_cont_put`.

Control flow: no implementation here. The functions are implemented/used by `cli.c` for handle hash lifecycle and reference management.

State/persistence: declares operations over `struct dc_cont` handle objects. These are in-memory client handles, not durable container metadata.

Dependencies/integration: included by container client modules that need internal handle lifecycle access without exposing it through public DAOS headers.

Risks: header is intentionally small; callers must honor reference-count conventions from the implementation.

Test signals: indirect via container open/close/global-handle tests.
