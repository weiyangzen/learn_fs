# sources/sync-backup/kopia/app/tests/main.spec.js

## Purpose
Playwright Electron end-to-end coverage for Kopia UI startup, tray menu behavior, repository window creation, configuration persistence, and app data isolation.

## APIs, Types, and Functions
Important APIs include dependencies `@playwright/test`, `playwright`, `fs`, `os`, `path`; functions `getKopiaUIDir`, `getMainPath`, `getExecutablePath`, `createTemporaryAppDataDir`, `launchApp`, `waitForKopiaToStartup`.

## Control Flow, State, and Persistence
Helpers locate the UI app, create a temporary app-data directory, launch Electron, wait for startup, drive test hooks such as tray popup/close, and assert windows/config files for default and non-default repositories. The tests create temporary app data and inspect generated config JSON/window state. They intentionally isolate repository IDs and cleanup through Playwright lifecycle.

## Dependencies and Integration
This file integrates with @playwright/test, playwright, fs, os, path and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Risks are packaging-layout assumptions, timing around Electron startup, and reliance on test-only hooks. Strong signals are real Electron launch and renderer/window/tray integration.
