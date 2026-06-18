# sources/sync-backup/kopia/app/public/notifications.js

## Purpose
Small Electron main-process helper for persisted desktop notification level. It defines disabled, warning/error-only, and all-notification levels and reads/writes the value through the shared app config module.

## APIs, Types, and Functions
Important APIs include dependencies `electron`, `./config.js`.

## Control Flow, State, and Persistence
`getNotificationLevel` lazily loads the level from config once, defaulting if absent. `setNotificationLevel` updates the cached value and persists it, allowing tray/menu code to decide whether to display repository notifications. State is a single cached `level` plus the app configuration file. The file imports Electron `app` and filesystem/path modules only to resolve config through `config.js`.

## Dependencies and Integration
This file integrates with electron, ./config.js and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Risks are stale cache if config changes externally and caller-side interpretation of numeric levels. Its signals are integration with `electron.js` tray refresh and notification-config IPC.
