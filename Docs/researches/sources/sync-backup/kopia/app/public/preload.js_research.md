# sources/sync-backup/kopia/app/public/preload.js

## Purpose
Electron preload bridge that exposes a tiny, context-isolated `window.kopiaUI` API to renderer code for directory selection and browsing.

## APIs, Types, and Functions
Important APIs include dependencies `electron`.

## Control Flow, State, and Persistence
At preload time, `contextBridge.exposeInMainWorld` publishes `chooseDirectory` and `browseDirectory`; these delegate to `ipcRenderer.invoke("select-dir")` and `ipcRenderer.invoke("browse-dir", path)` in the main process. No persistent state is kept. The security boundary is the exposed API shape, not mutable data.

## Dependencies and Integration
This file integrates with electron and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
The primary risk is widening renderer privileges if more IPC is added without validation. Existing surface is intentionally narrow and should be tested with Electron startup/render IPC coverage.
