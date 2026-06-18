# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyManager.java

## Purpose
`SecretKeyManager` is SCM's local manager for symmetric secret-key lifecycle: initialize from persisted state, generate keys, rotate keys, expose current/historical keys, and update replicated key state.

## Important APIs, Types, And Functions
Constructors accept `SecretKeyState`, `SecretKeyStore`, durations, and algorithm or a `SecretKeyConfig`. `checkAndInitialize()` loads non-expired persisted keys or generates a first key. `checkAndRotate(boolean force)` rotates when forced or current key age reaches the rotation duration. `getCurrentSecretKey()`, `getSecretKey(UUID)`, `getSortedKeys()`, and `reinitialize()` expose state.

## Control Flow
Initialization is synchronized and idempotent. It filters expired keys from the store, generates a new key if none remain, then calls `state.updateKeys()`. Rotation first initializes if needed, then creates a new key, filters out expired old keys, appends the new key, and updates state. Key generation uses `KeyGenerator.getInstance(algorithm)`, random UUID, current time, and expiry time.

## State, Persistence, And Dependencies
State is delegated to `SecretKeyState`; persistence is through `SecretKeyStore` invoked by state. The manager holds rotation/validity durations and a `KeyGenerator`. Dependencies include SCM exceptions and Java crypto/time APIs.

## Integration Points
SCM exposes this manager through secret-key protocol APIs. `SecretKeyState.updateKeys()` is annotated for Ratis replication, so rotations propagate to all SCMs.

## Risks
No validation ensures validity duration exceeds rotation duration. `getCurrentSecretKey()` may return null before initialization. `KeyGenerator` is stored and used inside synchronized methods; algorithm misconfig fails construction.

## Test Signals
Tests should cover first initialization, reload with expired filtering, forced and time-based rotation, no-op rotation, state persistence calls, reinitialization from leader snapshots, and invalid algorithm handling.
