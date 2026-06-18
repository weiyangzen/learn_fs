# File Research: sources/windows/dokany/dokan/mount.c

Implements service, registry, mount-point, unmount, and shell notification support for Dokan.

Key areas:
- Defines a local `REPARSE_DATA_BUFFER` for mount-point reparse point creation.
- Service helpers:
  - `DokanServiceExists`
  - `DokanServiceControl`
  - `DokanServiceInstall`
  - `DokanServiceDelete`
- Event log registry install/uninstall:
  - `DokanDriverEventLogInstall`
  - `DokanDriverEventLogUninstall`
- Network provider registry install/uninstall:
  - `DokanNetworkProviderInstall`
  - `DokanNetworkProviderUninstall`
- Mount-point helpers:
  - `CreateMountPoint`
  - `DeleteMountPoint`
  - `DokanMount`
  - `GenerateUnmountPoint`
  - `DokanRemoveMountPoint`
  - `DokanNotifyUnmounted`
- Drive-letter broadcast helpers:
  - `EnableTokenPrivilege`
  - `DokanBroadcastCallback`
  - `DokanBroadcastLink`

Important behavior:
- Directory mount points are created as `IO_REPARSE_TAG_MOUNT_POINT` reparse points pointing at `\??<DeviceName>\`.
- Drive-letter mounts notify applications and Explorer with `BroadcastSystemMessage` and `SHChangeNotify`.
- Non-drive mount cleanup removes the mount point unless mount manager was used.
- `DokanRemoveMountPoint` sends a global release IRP rather than directly deleting the reparse point.
- Unmount notification calls the filesystem’s `Unmounted` callback if present.

Risks and notes:
- Registry updates require admin rights and write under `HKLM`.
- Network provider order editing manipulates comma-delimited provider strings.
- Broadcast work is asynchronous via threadpool work to avoid hangs in message receivers.
