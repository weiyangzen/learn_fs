# sources/test-tools/kdevops/terraform/azure/scripts/vm_family_metadata.yml

## Purpose
This YAML file provides human-readable Azure VM family descriptions, help text, and workload examples for hierarchical VM-size Kconfig generation.

## Important APIs, Types, And Functions
Top-level keys are family prefixes such as `Standard_A`, `Standard_B`, `Standard_D`, `Standard_DS`, `Standard_E`, `Standard_ES`, `Standard_M`, `Standard_F`, `Standard_FS`, `Standard_L`, `Standard_LS`, `Standard_N`, `Standard_NC`, `Standard_ND`, `Standard_NV`, `Standard_H`, and `Standard_Dp`. Each entry can contain `description`, block `help_text`, and `workloads`.

## Control Flow
There is no code execution. `gen_kconfig_size` loads the file, looks up metadata by parsed family prefix, and falls back to generic descriptions if a family is missing.

## State And Persistence
The file persists curated documentation and policy text in the repo. Updating descriptions changes generated menu help but not cloud state.

## Dependencies And Integration Points
It depends on PyYAML parsing and the family-prefix parser in `gen_kconfig_size`. It integrates with `families.j2` output so menuconfig users see useful family descriptions.

## Risks And Test Signals
The "Last Updated" comment can become stale as Azure adds families. Missing families degrade help text quality but do not fail generation. YAML formatting or indentation errors can disable all metadata. Tests should parse the file, verify required fields for each family, compare discovered family prefixes against metadata coverage, and render a sample Kconfig menu.
