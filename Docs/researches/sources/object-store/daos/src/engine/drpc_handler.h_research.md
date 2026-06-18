# sources/object-store/daos/src/engine/drpc_handler.h

## Purpose
Declares the public internal interface for the dRPC handler registry. It documents how module-specific dRPC handlers are registered and how listener code dispatches incoming calls.

## Important APIs
The header declares initialization/finalization, single and bulk registration, lookup, single and bulk unregistration, and `drpc_hdlr_process_msg()`. It also documents that each handler is responsible for parsing `Drpc__Call`, acting on it, and filling a response even for errors.

## Control flow and integration
Consumers initialize the registry during engine startup, register handler arrays from modules, and pass incoming calls to `drpc_hdlr_process_msg()`. The listener/progress layer does not know module-specific behavior; it only creates responses and calls this dispatcher.

## State and persistence behavior
The header does not define state, but the implementation uses a process-local registry. No persistent state is associated with handler registration.

## Dependencies
Includes `daos/drpc.h` for protobuf dRPC call/response types and `daos_srv/daos_engine.h` for `struct dss_drpc_handler` and `drpc_handler_t` definitions.

## Risks
The contract that handlers always produce a response is important; a buggy handler can leave response status/body inconsistent. The API does not expose locking or ownership semantics, implying startup/shutdown-only mutation.

## Test signals
Compile tests ensure module handler arrays match the declared type. Unit tests should validate the documented error codes and that dispatch handles missing modules without crashing.
