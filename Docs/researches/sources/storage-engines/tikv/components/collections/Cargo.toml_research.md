# sources/storage-engines/tikv/components/collections/Cargo.toml

## Purpose
Cargo manifest for TiKV's lightweight `collections` component, which centralizes hash collection aliases using a faster hasher.

## APIs and control flow
The package is named `collections`, version `0.1.0`, edition 2021, Apache-2.0 licensed, and `publish = false`. There is no build script, binary target, feature definition, or dev dependency here.

## State, dependencies, and integration
Dependencies are `fxhash = "0.2.1"` and workspace `tikv_alloc`. `fxhash` backs the component's type aliases, while `tikv_alloc` keeps allocation behavior aligned with the broader TiKV workspace. The manifest integrates as a private workspace crate.

## Risks and test signals
FxHash is optimized for speed, not adversarial hash resistance; callers should not use this alias for untrusted attacker-controlled key sets without considering collision risks. The manifest itself has no tests. Validation comes from compiling dependents that import `collections::{HashMap,HashSet}`.
