# sources/sync-backup/kopia/app/sign.mjs

## Purpose
Windows signing helper for the Electron build. It invokes `signtool` with SHA-1 fingerprint and retry/backoff behavior around transient signing failures.

## APIs, Types, and Functions
Important APIs include dependencies `child_process`.

## Control Flow, State, and Persistence
The module builds signing arguments, loops attempts, runs child-process signing synchronously, sleeps between failures, and exits with the signing result once success or attempts are exhausted. State is limited to environment/configured certificate identity and attempt counters. The signed artifact is the durable output, outside this script.

## Dependencies and Integration
This file integrates with child_process and the surrounding Kopia UI packaging/runtime code.

## Risks and Test Signals
Risks are leaking signing configuration in logs, brittle `signtool` path assumptions, and retry masking persistent certificate/timestamp failures. Build pipeline execution is the main signal.
