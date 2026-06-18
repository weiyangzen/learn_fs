# sources/storage-engines/foundationdb/flow/EncryptUtils.cpp

## Purpose
Implements Flow encryption utility helpers for cipher-mode parsing, trace-key construction, encryption-header authentication token validation, random test-mode selection, and reserved encryption-domain checks.

## Important APIs, Types, And Functions
`encryptModeFromString()` maps persisted/configured mode strings to `EncryptCipherMode`. `getEncryptDbgTraceKey()` and `getEncryptDbgTraceKeyWithTS()` build TraceEvent field names containing domain, base-key, and timestamp data. `getEncryptHeaderAuthTokenSize()`, `isEncryptHeaderAuthTokenAlgoValid()`, `isEncryptHeaderAuthTokenModeValid()`, `isEncryptHeaderAuthTokenDetailsValid()`, and `getAuthTokenAlgoFromMode()` validate the token mode/algo pair. `getRandomAuthTokenMode()` and `getRandomAuthTokenAlgo()` support randomized simulation coverage. `isReservedEncryptDomain()` and `isEncryptHeaderDomain()` classify special domain ids.

## Control Flow
Most routines are direct validation or formatting helpers. Unsupported cipher modes and token sizes throw `not_implemented()`. `getAuthTokenAlgoFromMode()` lets `NONE` override the configured algorithm, otherwise reads `FLOW_KNOBS->ENCRYPT_HEADER_AUTH_TOKEN_ALGO`, rejects a non-none mode with none algorithm, asserts final consistency, and returns the selected algorithm.

## State And Persistence Behavior
The file owns no durable state. It interprets configuration from `FLOW_KNOBS`, uses deterministic randomness for simulation/test selection, and emits warning/detail TraceEvents for unsupported or inconsistent settings.

## Dependencies And Integration Points
It integrates with `flow/EncryptUtils.h`, `IRandom`, `Knobs`, and `Trace`; encryption domains and auth-token enums are consumed by storage/encryption code and by the `Knobs.cpp` encryption defaults.

## Risks And Edge Cases
Mode parsing is intentionally narrow (`NONE`, `AES-256-CTR`), so adding a cipher requires updating this switch. `getEncryptDbgTraceKey()` has a format string for the no-base-key case with more format placeholders than provided arguments, making trace-key formatting worth checking. Auth-token misconfiguration fails hard through `not_implemented()`, which is appropriate for unsupported combinations but sensitive to knob defaults.

## Test Signals
No local unit test exists in this file. Coverage comes from encryption users, simulation randomization via the random auth-token helpers, and trace/log assertions around token configuration.
