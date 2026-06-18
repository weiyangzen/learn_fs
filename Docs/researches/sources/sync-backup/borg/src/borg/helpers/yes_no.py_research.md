# sources/sync-backup/borg/src/borg/helpers/yes_no.py

## Purpose
Implements reusable yes/no/default prompting with environment overrides, retry behavior, JSON logging mode, and robust EOF/Unicode handling.

## Important APIs, Types, And Functions
Constants `FALSISH`, `TRUISH`, `DEFAULTISH`, and sentinel `ERROR`. Public function `yes(...)` supports prompt messages, accepted-answer messages, default behavior, retry control, environment override, custom output stream, injected input function, prompt suppression, and message id.

## Control Flow
`yes` prints an initial prompt if provided, then loops. If an env override is set, that value is used once and optionally reported. Otherwise it reads input unless prompting is disabled. EOF maps to the default answer; `UnicodeDecodeError` maps to an invalid sentinel. Answers are classified against defaultish/truish/falsish. Invalid answers optionally log an invalid message; retry false returns the default, retry true emits retry prompt and repeats, clearing a bad env override.

## State And Persistence
No module mutable state. It reads environment and writes to stderr or the provided stream. In JSON logger mode it prints structured question events to stderr.

## Dependencies And Integration Points
Used by passphrase verification and other interactive confirmations. Depends on the `borg` logger's `json` attribute convention.

## Risks And Edge Cases
Output mode changes with logger configuration. Empty string is defaultish by default. Environment overrides can bypass interactivity but are cleared after invalid input. Custom accepted-answer lists must not include the `ERROR` sentinel. Prompting with `prompt=False` returns default without reading.

## Test Signals
Existing yes/no tests should cover true/false/default answers, EOF, Unicode decode errors, retry/no-retry, env overrides, JSON output, prompt suppression, custom streams, and invalid defaults.
