# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/DefaultSecretKeySignerClient.java

## Purpose
`DefaultSecretKeySignerClient` fetches and caches the current SCM symmetric secret key for token signing, then periodically refreshes it after the configured rotation interval.

## Important APIs, Types, And Functions
The constructor accepts `SecretKeyProtocol` and thread name prefix. `start()` loads the initial key with retry and schedules polling. `getCurrentSecretKey()` returns the cached key and requires initialization. `refetchSecretKey()` forces a refresh check. `stop()` shuts down the scheduled executor. Helpers include `loadInitialSecretKey()`, `scheduleSecretKeyPoller()`, and synchronized `checkAndRefresh()`.

## Control Flow
Initial load retries `SECRET_KEY_NOT_INITIALIZED` with exponential backoff up to 100 retries. Polling computes next rotation from the cached key creation time plus rotate duration. Once the key is older than the rotate duration, it fetches SCM's current key and updates the atomic cache if changed.

## State, Persistence, And Dependencies
State is an atomic cached key, daemon thread factory, scheduled executor, and protocol reference. No persistence is local. Dependencies include secret-key config parsing, Hadoop retry policies, `RetriableTask`, and SCM secret-key exceptions.

## Integration Points
`DefaultSecretKeyClient` uses this for signer-side behavior. Token secret managers use the current key returned here to sign container/block tokens.

## Risks
If scheduled refresh throws `UncheckedIOException`, the scheduled task may stop depending on executor behavior. Negative initial delay can schedule immediately but should be tested. Long initial retry window can delay service startup. Cache access before `start()` throws `NullPointerException` via `requireNonNull`.

## Test Signals
Tests should cover initial retry on not-initialized, fail-fast on other errors, scheduled refresh timing, forced refetch, cache update/no-op, executor shutdown, and get-before-start failure.
