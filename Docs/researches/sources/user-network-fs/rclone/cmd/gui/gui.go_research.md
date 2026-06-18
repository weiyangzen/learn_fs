<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gui/gui.go -->
# sources/user-network-fs/rclone/cmd/gui/gui.go

## Purpose

`gui.go` implements `rclone gui`, serving the embedded or user-supplied rclone web UI and a paired RC API server, then opening an authenticated browser URL.

## Important APIs, Types, and Functions

Embedded `dist.zip` and `dist.tag` provide the default UI. Flags configure GUI address, API address, credentials, no-auth, browser opening, and metrics. The command resolves a GUI source with `guiSourceFS`, creates a GUI HTTP server, computes CORS origin with `originFromURL`, configures and starts an RC server, builds an SPA handler with `guiHandler`, serves compressed static assets, builds a login URL with `buildLoginURL`, optionally opens the browser, then waits for either server to exit and shuts both down.

## Control Flow

Source validation occurs before binding sockets. GUI and RC ports default to `localhost:0`. Auth credentials are generated unless disabled or supplied. The command blocks until one server stops.

## State and Persistence Behavior

It starts local HTTP listeners, may open a browser, reads embedded/zip/dir assets, and generates an in-memory random password. It does not write config.

## Dependencies and Integration Points

It integrates `lib/http`, `rcserver`, RC options, chi compression middleware, `open-golang`, systemd notification, embedded assets, zip/filesystem APIs, and the web app login contract.

## Risks and Test Signals

Risks include exposing no-auth API on non-local addresses, credentials in logged URLs, embedded zip missing, CORS origin mismatch, zip close leaks, SPA fallback serving wrong files, browser-open failures, and shutdown races. Tests should cover source FS variants, handler static/fallback/gzip behavior, login URL escaping, auth generation, metrics forwarding, and server lifecycle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gui/gui.go -->
