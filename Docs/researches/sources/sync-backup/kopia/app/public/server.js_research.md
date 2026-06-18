# sources/sync-backup/kopia/app/public/server.js

## Purpose
Main-process server manager for per-repository `kopia server start` child processes used by the UI. It builds process arguments, tracks status, polls the HTTPS API, tails server logs, and responds to renderer status fetch IPC.

## APIs, Types, and Functions
Important APIs include dependencies `electron`, `./utils.js`, `child_process`, `electron-log`, `./config.js`; functions `newServerForRepo`.

## Control Flow, State, and Persistence
`newServerForRepo` lazily constructs a server object with mutable status fields. It spawns the selected Kopia binary with repository-specific cache/log paths, captures generated server details from stdout/logs, polls `/api/v1/status`, emits status updates, and exposes `serverForRepo` lookup plus IPC refresh handling. The module keeps a `servers` map keyed by repository ID, active child process handles, address/certificate/password/control-password details, status polling intervals, and a bounded in-memory log buffer. State is process-local but depends on repo config files and server-generated credentials/certificates.

## Dependencies and Integration
This file integrates with electron, ./utils.js, child_process, electron-log, ./config.js and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Important risks are leaking child processes or intervals, trusting parsed log details, certificate/password mismatch between runs, and UI reporting stale status after process exit. Integration signals are IPC `status-fetch`, status update messages to Electron, and server log/status transitions.
