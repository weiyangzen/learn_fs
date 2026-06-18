# File Research: sources/windows/dokany/sys/except.c

Provides Dokan's structured exception filter and fallback IRP completion handler for expected NTSTATUS exceptions.

Key entry points:
- `DokanExceptionFilter()` logs exception and context records, catches only exceptions considered expected by `FsRtlIsNtstatusExpected()`, and otherwise continues exception search.
- `DokanExceptionHandler()` validates the target VCB, maps unmount state to `STATUS_NO_SUCH_DEVICE`, and completes the IRP unless the exception status is `STATUS_PENDING`.

Core mechanics:
- Expected filesystem exceptions are converted into normal handler execution.
- Unexpected exceptions are deliberately passed to a higher-level handler.
- IRPs are completed with zero `IoStatus.Information` on handled failures.
- Invalid/missing VCB state maps to `STATUS_INVALID_PARAMETER`.

Filesystem relevance:
- This is defensive kernel-driver error containment around Dokan IRP dispatch paths.

Notable risks:
- It assumes `DeviceObject->DeviceExtension` is a VCB for handled IRPs; unusual device-object contexts fall back to invalid parameter.
- `STATUS_PENDING` is not completed, preserving ownership semantics for paths where another component owns the IRP.
