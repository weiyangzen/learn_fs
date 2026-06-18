# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/controller.c

## Purpose

`controller.c` implements I/O manager controller object wrappers over kernel device queues.

## Main Functions

- `IoAllocateController()`:
  - Requires `DISPATCH_LEVEL`.
  - Stores caller context and execution routine in the device object's wait context block.
  - Inserts the WCB into the controller's device wait queue.
  - If the queue was not busy, immediately calls the execution routine with the device object's current IRP.
  - Frees the controller if the routine returns `DeallocateObject`.
- `IoCreateController()`:
  - Creates a kernel controller object with optional extension space.
  - Inserts it into the object manager, closes the temporary handle, zeroes the object, initializes type/size/extension pointer, initializes the device queue, and returns the controller pointer.
- `IoDeleteController()` dereferences the controller object.
- `IoFreeController()` removes the next queued device, invokes its stored execution routine, and recursively frees again if requested.

## Important Details

- The controller extension is placed immediately after the `CONTROLLER_OBJECT`.
- Queue entries are recovered back to `DEVICE_OBJECT` through `DEVICE_OBJECT.Queue.Wcb.WaitQueueEntry`.
- Execution routines receive `NULL` for the map-register base argument in this controller path.

## Research Notes

This is legacy controller-serialization infrastructure. It is relevant to storage-driver scheduling concepts but independent from the VFAT driver code in this batch.
