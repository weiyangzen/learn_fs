<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/LoginCounter.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/LoginCounter.cs

## Purpose
`LoginCounter` provides in-memory rate limiting for repeated failed authentication attempts per user.

## Important APIs and Types
`LoginEntry` stores a window start timestamp and attempt count. The constructor accepts `maxLoginAttemptsInWindow` and `loginWindowDuration`. `HasRemainingLoginAttempts(userID)` checks without incrementing; `HasRemainingLoginAttempts(userID, incrementCount)` optionally records an attempt.

## Control Flow
The method locks the dictionary, looks up or creates an entry, resets expired windows, increments only when requested, and returns whether the current attempt count is below the configured maximum.

## State, Dependencies, and Integration
State is process-local and not persisted. `IndependentNTLMAuthenticationProvider` uses lowercased usernames to lock out invalid usernames or failed passwords after many attempts. The lock on `m_loginEntries` makes dictionary mutation thread-safe for concurrent SMB logins.

## Risks and Test Signals
The threshold check uses `< max`, so the attempt that reaches the limit returns false. Entries are never pruned, which can grow with many usernames. Restarting the process clears lockouts. Tests should cover check-without-increment, boundary attempt counts, window expiration, case normalization by callers, and concurrent increments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/LoginCounter.cs -->
