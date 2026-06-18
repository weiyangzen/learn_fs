<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_s3.rs -->
# sources/object-store/rustfs/crates/obs/examples/test_dial9_s3.rs

## Purpose
Manually validates dial9 S3 configuration handling. It focuses on bucket and prefix fields under default and environment-derived configs.

## Important APIs, Types, and Functions
Uses `Dial9Config::default`, `Dial9Config::from_env`, and `is_enabled`. It asserts default S3 bucket and prefix are `None`, prints the `RUSTFS_RUNTIME_DIAL9_ENABLED` env var, and displays configured S3 upload state.

## Control Flow
The example first checks default config, then reports enabled state, then loads environment config. If dial9 is disabled, it skips S3-specific enabled assertions and prints instructions. If enabled, it prints whether S3 upload is active and any bucket/prefix values.

## State and Persistence
No dial9 session is started and no S3 upload occurs. It only reads configuration.

## Dependencies and Integration
Integrates with dial9 config parsing through the `rustfs_obs` crate-root re-export. It documents required environment variables for S3 testing.

## Risks
The example validates config presence but not credentials, upload permissions, object key formation, or network behavior. As with other examples, console PASS output is manual-test oriented.

## Test Signals
Assertions ensure default S3 fields are absent. Manual output confirms env-derived S3 settings when dial9 is enabled.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_s3.rs -->
