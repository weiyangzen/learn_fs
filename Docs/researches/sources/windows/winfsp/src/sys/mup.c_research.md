# File Research: sources/windows/winfsp/src/sys/mup.c

## Purpose

`mup.c` implements WinFsp's filesystem MUP redirector device support. It registers volume prefixes, answers network redirector prefix-resolution IOCTLs, and forwards IRPs arriving at the fsmup device to the appropriate fsvol device.

## Main Contents

- `FSP_MUP_PREFIX_CLASS` is enabled, so WinFsp claims class prefixes like `\ClassName` instead of only full prefixes like `\ClassName\InstanceName`.
- `FSP_MUP_CLASS` tracks class-prefix refcounts and prefix-table entries.
- Functions:
  - `FspMupGetClassName`
  - `FspMupRegister`
  - `FspMupUnregister`
  - `FspMupGetFsvolDeviceObject`
  - `FspMupHandleIrp`
  - `FspMupRedirQueryPathEx`

## Prefix Registration

`FspMupRegister`:

- Extracts the class prefix from the fsvol `VolumePrefix`.
- Allocates a class record.
- Inserts the full volume prefix into `PrefixTable`.
- References the fsvol device object while registered.
- Inserts or refcounts the class entry in `ClassTable`.

`FspMupUnregister` reverses this:

- Removes the full prefix.
- Dereferences the fsvol device.
- Decrements and possibly removes/frees the class record.

Both operations are protected by the fsmup prefix-table lock.

## IRP Handling

`FspMupHandleIrp`:

- Enters filesystem context.
- Special-cases `IRP_MJ_CREATE` with empty name as an open of the fsmup device itself and completes it with `STATUS_SUCCESS`.
- For other creates, follows related file objects to the root and resolves the filename against the prefix table.
- Special-cases `IRP_MJ_DEVICE_CONTROL` with `IOCTL_REDIR_QUERY_PATH_EX` and handles it locally.
- For all other requests, tries to recover the fsvol device from `FileObject->FsContext` or `FsContext2`.
- If an fsvol target is found, skips the current stack location and calls the fsvol driver.
- If no target is found, completes locally with status chosen by major function.

## Prefix Resolution

`FspMupRedirQueryPathEx`:

- Accepts only kernel-mode callers.
- Validates input and output buffers.
- With class-prefix mode enabled, extracts the class from the query path and succeeds if that class is registered.
- Sets `QUERY_PATH_RESPONSE.LengthAccepted` to the class prefix length.

## Notable Details

- For unresolved creates, the code returns `STATUS_BAD_NETWORK_PATH`, specifically to satisfy DFS/MUP behavior around `\ClassName\IPC$` probes.
- Cleanup and close without a target return success because their status is ignored except for pending.
- Query/set information without a target return `STATUS_INVALID_PARAMETER`; other unhandled IRPs return `STATUS_INVALID_DEVICE_REQUEST`.
- Class-prefix claiming improves resolution speed for known classes but prevents another redirector from owning shares under the same class prefix.
