# sources/test-tools/kdevops/scripts/lambdalabs_infer_region.py

## Purpose
`lambdalabs_infer_region.py` is a backward-compatible wrapper that chooses a Lambda Labs region for a requested instance type by invoking `lambda-cli`.

## Important APIs, Types, And Functions
Functions are `get_best_region_for_instance(instance_type)` and `main()`. It shells out to the sibling `lambda-cli` executable.

## Control Flow
The wrapper runs `lambda-cli --output json instance-types list`, parses the JSON, and if the requested instance name is present, runs `lambda-cli --output json smart-select --mode cheapest`. If that succeeds without an error field, it returns the selected region. Any subprocess or JSON failure falls back to `us-west-1`. With no exact CLI argument, `main()` prints `us-west-1` and exits success.

## State And Persistence
No files are written. Output is a single region string intended for shell/Kconfig consumption.

## Dependencies And Integration Points
Depends on `subprocess`, `json`, `os`, `sys`, and a working `lambda-cli`. Used by older Kconfig shell commands that expect a region inference helper.

## Risks And Edge Cases
The selected region is not specifically guaranteed to support the requested instance; it only checks that the instance exists before returning the global cheapest smart selection. If `lambda-cli` has syntax/runtime errors, this silently returns `us-west-1`. No stderr diagnostics are emitted.

## Test Signals
Mock subprocess outputs for matching instance, missing instance, CLI failure, invalid JSON, smart-select error, no arguments, and verify fallback behavior.
