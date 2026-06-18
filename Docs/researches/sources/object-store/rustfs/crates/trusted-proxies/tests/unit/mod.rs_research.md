# sources/object-store/rustfs/crates/trusted-proxies/tests/unit/mod.rs

Purpose: Unit test module registry for trusted-proxies.

Important APIs: Under `#[cfg(test)]`, declares `config_tests`, `ip_tests`, `validation_tests`, and `validator_tests`.

Control flow and state: Compile-time test wiring only.

Integration points: Ensures unit test modules are included when this module target is compiled.

Risks and tests: No runtime behavior. New unit test files require registration here unless compiled as separate integration targets.
