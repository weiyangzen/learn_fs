# sources/sync-backup/kopia/app/public/electron.js

## Purpose
Electron main-process entry point for Kopia UI. It owns tray lifecycle, repository BrowserWindow instances, app startup/login handling, native notifications, update checks, release-note launching, dock/tray presentation, and IPC-driven menu refreshes.

## APIs, Types, and Functions
Important APIs include dependencies `electron-updater`, `./utils.js`, `./server.js`, `electron-store`, `electron-log`, `path`, `crypto`; functions `getDisplayConfiguration`, `showRepoWindow`, `checkForUpdates`, `checkForUpdatesNow`, `installUpdate`, `viewReleaseNotes`, `isOutsideOfApplicationsFolderOnMac`, `maybeMoveToApplicationsFolder`, `updateDockIcon`, `showAllRepoWindows`.

## Control Flow, State, and Persistence
Startup initializes single-instance behavior, creates a tray on `app.ready`, loads repository configuration, starts/opens repository windows through `showRepoWindow`, and rebuilds tray menus when server, autostart, or notification state changes. Auto-updater callbacks mutate cached update state and the menu exposes check/download/install actions. State is mainly process-global: `tray`, `repositoryWindows`, `repoIDForWebContents`, update status variables, Electron Store persisted window bounds, last-notified version, and repository credentials passed to server/window helpers. It also persists display-aware window placement and relies on app-data paths for logs.

## Dependencies and Integration
This file integrates with electron-updater, ./utils.js, ./server.js, electron-store, electron-log, path, crypto and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Risks cluster around stale window/server mappings, persisted bounds outside current displays, update notification duplication, macOS application-folder migration, and credential handling in IPC/window creation. Test hooks in development expose tray/window handles for Playwright coverage.
