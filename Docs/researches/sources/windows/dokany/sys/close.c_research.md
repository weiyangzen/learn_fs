# File Research: sources/windows/dokany/sys/close.c

## Role

Handles `IRP_MJ_CLOSE`, releases kernel per-open state, and sends a best-effort close notification to user mode.

## Main Function

- `DokanDispatchClose`

## Behavior

- Validates file object and context.
- If CCB validation fails but a CCB exists, frees CCB and FCB defensively.
- If user-mode dispatch is blocked for the FCB, frees CCB/FCB and returns success.
- Otherwise:
  - Allocates an `EVENT_CONTEXT`.
  - Copies CCB user context and FCB filename into the close event.
  - Frees the CCB and FCB immediately.
  - Sends a notification with `DokanEventNotification`.
- Close IRPs are never registered as pending.

## Dependencies

- `dokan.h`
- `util/fcb.h`
- CCB/FCB allocation lifecycle.
- User-mode notification queue.

## Notes and Risks

- Close is always completed synchronously from the kernel side.
- If event allocation fails, the code still frees kernel state and returns success, so close notification can be lost.
- Distinct from cleanup: cleanup handles semantic close from user handles; close releases object references.
