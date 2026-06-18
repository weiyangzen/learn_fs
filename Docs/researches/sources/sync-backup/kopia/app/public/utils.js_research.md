# sources/sync-backup/kopia/app/public/utils.js

## Purpose
Shared Electron utility module for OS-specific resource paths and executable/icon selection.

## APIs, Types, and Functions
Important APIs include dependencies `electron`, `path`.

## Control Flow, State, and Persistence
It computes `osShortName`, resolves public and icons paths relative to the module, chooses the default Kopia server binary for the platform, and exposes `selectByOS` to select per-OS values. State is static process configuration derived from `process.platform`, `app.isPackaged`, and module paths. No repository state is persisted here.

## Dependencies and Integration
This file integrates with electron, path and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Risks are packaging path drift, unsupported platform defaults, and icon/binary names diverging from build artifacts. It integrates directly with tray creation and server child-process launching.
