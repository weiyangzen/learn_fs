# File Research: sources/windows/winfsp/src/dll/fsctl.c

Driver and Service Control Manager interface layer for WinFsp filesystem devices.

Key responsibilities:
- Creates WinFsp volumes by constructing a `GLOBALROOT` device path with encoded volume parameters.
- Starts the WinFsp driver service before opening volumes.
- Retrieves volume names and volume lists through driver control codes.
- Sends transaction, stop, notify, mountdev, mountmgr, unload, and list IOCTL/FSCTL requests.
- Detects installed driver version and switches between older `FSP_FSCTL_TRANSACT*` and newer `FSP_IOCTL_TRANSACT*` control codes.
- Starts and stops driver services with side-by-side installation awareness.
- Enumerates WinFsp filesystem driver services.
- Registers and unregisters the filesystem driver service.
- Updates service security so Everyone can start but not stop the service.

Important behavior:
- `FspFsctlCreateVolume` encodes raw `FSP_FSCTL_VOLUME_PARAMS` bytes into Unicode private-use characters appended to the device path.
- Non-SxS mode tries the normal driver service first, then selects the best available SxS service if needed.
- SxS mode starts only the suffixed driver name.
- Container detection short-circuits service start/stop as successful.
- `FspFsctlStopService` temporarily enables/checks `SeLoadDriverPrivilege` before sending unload.
- `FspFsctlRegister` derives the `.sys` driver path from the module path and creates or updates a demand-start filesystem driver service.

Dependencies:
- Includes `dll/library.h` and `aclapi.h`.
- Uses Windows SCM APIs, registry/token/privilege APIs, service security APIs, `DeviceIoControl`, `CreateFileW`, and WinFsp SxS helpers.

Notable risks:
- Service registration, stop, unload, and security changes require administrative/privileged context.
- Device-path construction has strict `MAX_PATH` and encoded-parameter size checks.
- The service security policy is deliberately unusual: broad start permission and broad stop denial.
