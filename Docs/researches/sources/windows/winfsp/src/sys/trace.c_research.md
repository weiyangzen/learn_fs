# File Research: sources/windows/winfsp/src/sys/trace.c

## Purpose

`trace.c` provides optional debug tracing support when `FSP_TRACE_ENABLED` is enabled. It prints compact function/file/line traces and enriches insufficient-resource traces with low-memory event state.

## Main Contents

Compiled only under `#if FSP_TRACE_ENABLED`:

- `FspTrace`
- `FspTraceNtStatus`
- `FspOpenEvent`
- `FspCloseEvent`
- `FspTraceInitialize`
- `FspTraceFinalize`

## Behavior

`FspTrace`:

- Strips directory components from the source file path.
- Asserts IRQL is no higher than dispatch level.
- Prints `DRIVER_NAME`, function, file, and line through `DbgPrintEx`.

`FspTraceNtStatus`:

- Also strips source path.
- For `STATUS_INSUFFICIENT_RESOURCES`, checks kernel low-memory condition events and prints a three-character memory state:
  - memory,
  - nonpaged pool,
  - paged pool.
- For other statuses, prints the hex status.

`FspTraceInitialize` opens and references:

- `\KernelObjects\LowMemoryCondition`
- `\KernelObjects\LowNonPagedPoolCondition`
- `\KernelObjects\LowPagedPoolCondition`

`FspTraceFinalize` dereferences and closes any opened events.

## Integration

This file supports tracing macros such as `FSP_TRACE()` and status-tracing sites elsewhere in the driver. It uses object-manager event handles and `ObReferenceObjectByHandle`.

## Notable Details

- It locally redefines `STATUS_INSUFFICIENT_RESOURCES` after undefining it, likely to avoid macro/header inconsistencies in trace builds.
- If low-memory events cannot be opened, tracing still works but omits those event states.
