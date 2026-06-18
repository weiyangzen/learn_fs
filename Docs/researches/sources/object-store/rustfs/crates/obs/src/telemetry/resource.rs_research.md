<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/resource.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/resource.rs

Purpose: Builds the shared OpenTelemetry `Resource` used by RustFS telemetry providers so all emitted traces, metrics, and logs carry consistent service identity and host/network metadata.

Important APIs/types/functions: `build_resource(config)` returns an `opentelemetry_sdk::Resource`. It sets `service.name`, `service.version`, `deployment.environment.name`, and `network.local.address` using config values with RustFS defaults.

Control flow: The builder takes `service_name`, `service_version`, and `environment` from `OtelConfig` when present, falling back to `APP_NAME`, `SERVICE_VERSION`, and `ENVIRONMENT`. It calls `get_local_ip_with_default()` for the host address and attaches semantic-convention attributes under `SCHEMA_URL`.

State/persistence behavior: Stateless aside from the current host IP lookup. It does not cache resources, mutate globals, or persist anything.

Dependencies/integration: Uses `OtelConfig`, OpenTelemetry semantic conventions (`SERVICE_VERSION`, `DEPLOYMENT_ENVIRONMENT_NAME`, `NETWORK_LOCAL_ADDRESS`), `Resource::builder`, RustFS config constants, and `rustfs_utils::get_local_ip_with_default`. `otel.rs` calls this once and clones the resource into enabled providers.

Risks/test signals: Local IP discovery can vary by network environment and may expose node-level address data in telemetry. Service name is converted through `Cow` and `to_string`, so non-static config values are copied safely. There are no direct unit tests for resource attributes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/resource.rs -->
