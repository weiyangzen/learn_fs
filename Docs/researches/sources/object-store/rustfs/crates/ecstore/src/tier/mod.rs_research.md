# sources/object-store/rustfs/crates/ecstore/src/tier/mod.rs

## Purpose

Module barrel for ECStore tiering support.

## Important APIs and Types

Declares `tier`, `tier_admin`, `tier_config`, `tier_gen`, `tier_handlers`, `warm_backend`, and provider modules for Aliyun, Azure, GCS, Huawei Cloud, MinIO, R2, RustFS, S3, AWS SDK S3, and Tencent.

## Control Flow

No runtime control flow; it controls compile-time module visibility.

## State and Persistence Behavior

No state. Child modules own config, driver cache, and remote backend clients.

## Dependencies and Integration Points

Adding or selecting providers requires declarations here plus config/factory updates.

## Risks and Edge Cases

Both transition-client S3 and AWS SDK S3 modules are declared, but the visible factory selects the transition-client implementation.

## Test Signals

No direct tests; compile and child-module tests provide coverage.
