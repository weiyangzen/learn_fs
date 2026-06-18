# sources/test-tools/kdevops/scripts/lambdalabs_smart_inference.py

## Purpose
`lambdalabs_smart_inference.py` is a backward-compatible Kconfig shell helper that exposes the `lambda-cli smart-select --mode cheapest` result as individual `instance`, `region`, or `price` values.

## Important APIs, Types, And Functions
Functions are `get_smart_selection()` and `main()`. It shells out to sibling `lambda-cli` and returns a small dict with `instance_type`, `region`, and `price_per_hour` keys.

## Control Flow
`get_smart_selection()` invokes `lambda-cli --output json smart-select --mode cheapest`, parses stdout, and returns the data if no `error` field is present. On subprocess or JSON failure it returns defaults: `gpu_1x_a10`, `us-west-1`, `$0.75`. `main()` requires a query type and prints the requested field or errors on unknown query types.

## State And Persistence
No persistence. Output is a single text value for use in Kconfig or shell contexts.

## Dependencies And Integration Points
Depends on `subprocess`, `json`, `os`, and `sys`, plus a working `lambda-cli`. It bridges newer CLI logic into older Kconfig shell snippets.

## Risks And Edge Cases
If `lambda-cli` is broken or unauthenticated, defaults are silently used, which can lead to provisioning unavailable capacity. Price default is static. Unknown query types exit nonzero.

## Test Signals
Mock subprocess success, CLI error JSON, invalid JSON, subprocess failure, missing query type, valid `instance`/`region`/`price`, and unknown query type.
