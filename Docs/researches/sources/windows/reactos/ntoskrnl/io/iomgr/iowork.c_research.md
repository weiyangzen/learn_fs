# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iowork.c

## Purpose

Implements I/O manager wrappers around executive work items for device-associated deferred work.

## Key Functions

- `IoAllocateWorkItem` allocates an `IO_WORKITEM`, stores the target device object, and initializes the embedded executive work item to call `IopWorkItemCallback`.
- `IoQueueWorkItem` references the device object, records the caller’s worker routine and context, and queues the work item to the requested work queue.
- `IopWorkItemCallback` invokes the stored worker routine and dereferences the device object after the callback returns.
- `IoFreeWorkItem` frees the work item with pool tag `TAG_IOWI`.

## Filesystem Relevance

Provides the standard deferred execution mechanism for I/O components, including filesystems, filters, and storage drivers that need to run work outside the original call path.

## Dependencies and Coupling

Depends on executive work queues, object referencing for device lifetime protection, nonpaged pool allocation, and `IO_WORKITEM` layout.

## Research Notes

- Device lifetime is protected across queued work by reference/dereference around the queued callback.
- The work item itself is not freed after callback; ownership remains with the caller, which must call `IoFreeWorkItem`.
