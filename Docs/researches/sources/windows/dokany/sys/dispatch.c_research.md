# File Research: sources/windows/dokany/sys/dispatch.c

## Role

Provides top-level IRP dispatch wrapping, request-context construction, read-only enforcement, exception handling, and routing to per-major-function handlers.

## Main Functions

- `DokanBuildRequest`
- `DokanCancelCreateIrp`
- `DokanBuildRequestContext`
- `DokanDispatchRequest`

## Behavior

- `DokanBuildRequest`:
  - Enters filesystem context with `FsRtlEnterFileSystem`.
  - Sets top-level IRP when needed.
  - Calls `DokanDispatchRequest`.
  - Handles exceptions through Dokan exception filter/handler.
- `DokanBuildRequestContext`:
  - Captures device object, IRP, stack location, process ID, top-level status.
  - Resolves device extension type into global/DCB/VCB pointers.
  - Initializes `IoStatus.Information` to zero.
- `DokanDispatchRequest`:
  - Rejects most operations if the device is unmounted.
  - Enforces read-only volume behavior for write-like major functions.
  - Routes major functions to the corresponding `DokanDispatch*` handler.
- `DokanCancelCreateIrp`:
  - Completes a create IRP with a synthesized `EVENT_INFORMATION` status from a safe filesystem context.

## Dependencies

- `dokan.h`
- All per-operation dispatch functions.
- FsRtl top-level IRP conventions.
- Dokan exception handling and logging.

## Notes and Risks

- This is the common choke point for all IRP major functions.
- `REQUEST_CONTEXT` exists to avoid reading IRP stack/device state later after cancellation or ownership transfer.
- Read-only enforcement here is broad, while create-specific read-only checks live in `create.c`.
