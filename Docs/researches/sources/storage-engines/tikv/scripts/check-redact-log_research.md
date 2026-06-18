# sources/storage-engines/tikv/scripts/check-redact-log

## Purpose
Guards against logging user data through direct uppercase hex encoding. It requires redaction-aware wrappers for info logs and error messages.

## Important Commands and Control Flow
The script prints remediation guidance recommending `log_wrappers::Value()` or `log_wrappers::hex_encode_upper`. On Darwin it searches for `encode_upper` and filters out `log_wrappers`; elsewhere it uses GNU grep negative lookbehind for `(?<!hex_)encode_upper`. It excludes `hex.rs`, `tikv-ctl`, and `target`. Any match exits 1; no matches prints `Security check passed.`

## State, Dependencies, Integration
It is read-only and depends on bash, grep, platform regex behavior, and TiKV logging wrapper names. It integrates with CI security linting for `security.redact-info-log` compliance.

## Risks and Test Signals
The Darwin path is less precise than GNU grep. Aliases or wrapper renames can evade or break the policy. Direct `hex::encode_upper` should fail; wrapper-based calls should pass.
