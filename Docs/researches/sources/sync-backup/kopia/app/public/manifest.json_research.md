# sources/sync-backup/kopia/app/public/manifest.json

## Purpose
Web app manifest shipped with the React/Electron UI assets. It declares app names, icon files, standalone display mode, start URL, and theme/background colors.

## APIs, Types, and Functions
Important APIs include manifest keys `short_name`, `name`, `icons`, `start_url`, `display`, `theme_color`, and `background_color`.

## Control Flow, State, and Persistence
The file is static JSON consumed by the browser/runtime asset pipeline; there is no executable control flow. It points at `favicon.ico`, `logo192.png`, and `logo512.png` in the public asset directory and carries no mutable state.

## Dependencies and Integration
This file integrates with the web app manifest/runtime asset pipeline and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
The names still use Create React App placeholders, which can affect install/PWA metadata if surfaced outside Electron. Test signal is asset existence and successful app packaging.
