# sources/object-store/rustfs/crates/kms/src/service_manager.rs

## Purpose
Manages dynamic KMS configuration, lifecycle, health, and zero-downtime reconfiguration using versioned service instances.

## Important APIs, Types, And Functions
`KmsServiceStatus` captures not configured, configured, running, and error states. `KmsServiceManager` stores current versioned service in `ArcSwap<Option<ServiceVersion>>`, configuration/status in Tokio `RwLock`s, a monotonic `AtomicU64` version counter, and a lifecycle `Mutex`. Public methods include `configure`, `start`, `stop`, `reconfigure`, `get_manager`, `get_encryption_service`, `get_service_version`, and `health_check`. Global helpers use a `OnceLock<Arc<KmsServiceManager>>`.

## Control Flow
`configure` validates before mutating state. `start` serializes through the lifecycle mutex, requires a stored config, creates backend/manager/service, atomically publishes the new service, and marks running. `stop` atomically clears the current service but leaves configuration available. `reconfigure` validates, stores the new config, creates a new service version without stopping old references, atomically swaps it in, and keeps old operations alive through `Arc` ownership.

## State And Persistence
State is in-memory process-global service state; it does not persist config itself. `ArcSwap` lets readers get the current service without awaiting locks, while lifecycle operations remain serialized.

## Dependencies And Integration
Constructs `LocalKmsBackend`, `VaultKmsBackend`, or `VaultTransitKmsBackend` from `BackendConfig`, then wraps them in `KmsManager` and `ObjectEncryptionService`. Logging uses structured tracing fields for KMS service state events.

## Risks And Edge Cases
If `create_service_version` fails during reconfigure, the config has already been replaced and status becomes error while the previously published service may still be present in `current_service`; callers using `get_encryption_service` can still receive the old service. This may be intentional for availability but creates config/status/service skew to monitor. Version counter increments before backend creation, so failed attempts consume version numbers.

## Test Signals
Tests in this file verify invalid default local config is rejected before state update. Additional lifecycle, versioning, and concurrent reconfiguration tests live in `lib.rs`.
