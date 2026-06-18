# sources/test-tools/kdevops/scripts/lambdalabs_api.py

## Purpose
`lambdalabs_api.py` is the Lambda Labs API/Kconfig generation library. It fetches instance type capacity, derives regions, fetches images, provides hardcoded pricing, sanitizes names into Kconfig symbols, and emits generated Kconfig choices and mappings for kdevops Terraform configuration.

## Important APIs, Types, And Functions
Exports include `get_api_key()`, `make_api_request()`, `get_instance_types_with_capacity()`, `get_regions()`, `get_images()`, `sanitize_kconfig_name()`, `get_instance_pricing()`, `generate_instance_types_kconfig()`, `generate_instance_type_mappings()`, `generate_regions_kconfig()`, `generate_images_kconfig()`, and `main()`. Constant `LAMBDALABS_API_BASE` points at `https://cloud.lambdalabs.com/api/v1`.

## Control Flow
API helpers issue authenticated GET requests with urllib and return parsed JSON or safe empty collections on failure. Instance Kconfig generation fetches instance data and capacity, falls back to default choices when unavailable, sorts available/unavailable types, emits `choice` entries with region dependencies and help text, and omits the final string config because it is defined elsewhere. Region generation derives capacity counts and defaults to the most-capable region. Image generation mostly documents that current Terraform provider OS image selection is unsupported. `main()` prints requested generated content or writes all generated files to an output directory.

## State And Persistence
No module-level mutable state beyond constants. `main all` writes `Kconfig.compute.generated`, `Kconfig.location.generated`, and `Kconfig.images.generated`. API key retrieval delegates to the credentials module.

## Dependencies And Integration Points
Depends on `lambdalabs_credentials.py`, Python standard `urllib`, `json`, `os`, `sys`, and typing. It is imported by `lambda-cli`, capacity/tier scripts, SSH tooling patterns, and Kconfig generation workflows.

## Risks And Edge Cases
Pricing is hardcoded and labeled as 2025 data, so it can drift. API schema assumptions vary between dict and string region representations. Fallbacks hide API failures by generating default options. `get_api_key()` docstring mentions environment variables, but current credentials helper does not read `LAMBDALABS_API_KEY` directly. The generated Kconfig depends on external symbol names like `TERRAFORM_LAMBDALABS_REGION_MANUAL`.

## Test Signals
Mock `make_api_request()` for available/unavailable capacity, missing data, region dict/string shapes, empty images, and API failures. Validate generated Kconfig syntax, symbol sanitization, default selection, mapping lines, and `main all` output files.
