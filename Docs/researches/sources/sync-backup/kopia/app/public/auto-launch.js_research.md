# sources/sync-backup/kopia/app/public/auto-launch.js

## Purpose
Implements Electron main-process helpers for enabling, disabling, and querying KopiaUI launch-at-startup behavior.

## APIs, Functions, and Control Flow
The module imports `ipcMain` from Electron, `electron-log`, and `auto-launch`. It constructs an `AutoLaunch` instance named `Kopia`, using a macOS LaunchAgent. Module state `enabled` caches the current launch-at-startup status. `willLaunchAtStartup()` returns the cached value. `toggleLaunchAtStartup()` calls `autoLauncher.disable()` or `.enable()` based on the cache, logs the operation, updates `enabled`, and emits `launch-at-startup-updated` on success. Errors are logged. `refreshWillLaunchAtStartup()` calls `isEnabled()`, refreshes the cache, and emits the same update event.

## State, Persistence, and Dependencies
Persistent state is owned by platform auto-start mechanisms: LaunchAgent on macOS and the platform-specific behavior of `auto-launch` elsewhere. In-process state is the `enabled` cache, synchronized asynchronously from platform state. IPC events notify other main-process listeners or renderer bridges that UI state should refresh.

## Risks and Test Signals
Because toggles are asynchronous and the cache updates only on promise success, rapid repeated toggles can race against stale `enabled` state. The code emits through `ipcMain.emit`, which is suitable for internal main-process eventing but not direct renderer IPC unless bridged elsewhere. Test coverage likely comes from Electron UI E2E paths rather than unit tests for this module.
