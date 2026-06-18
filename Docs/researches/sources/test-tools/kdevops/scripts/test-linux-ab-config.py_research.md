# sources/test-tools/kdevops/scripts/test-linux-ab-config.py

## Purpose
Verifies that the current kdevops configuration enables Linux A/B testing and produces different baseline and development kernel refs.

## Important APIs
`LinuxABTester` tracks `failed_checks`. Methods are `check_config_file()`, `check_extra_vars()`, `verify_refs()`, `check_makefile_structure()`, and `run_checks()`. `main()` enforces execution from a kdevops root by requiring `Kconfig`.

## Control flow
The runner reads `.config`, requires `CONFIG_KDEVOPS_BASELINE_AND_DEV=y` and `CONFIG_BOOTLINUX_AB_DIFFERENT_REF=y`, reads `extra_vars.yaml`, extracts `target_linux_ref` and `target_linux_dev_ref` with regexes, verifies they are non-empty and distinct, and optionally checks `workflows/linux/Makefile` target names.

## State and dependencies
Read-only over `.config`, `extra_vars.yaml`, and optionally `workflows/linux/Makefile`. Uses Python standard library. The imported `subprocess` and `Path` are unused.

## Integration points
Useful in CI or local developer checks after `make` or `make extra_vars.yaml` generation for Linux A/B workflows.

## Risks and test signals
It parses YAML as text, so quoting/comments are not interpreted structurally. Output includes Unicode symbols, which may be noisy in minimal terminals. Test success should exit 0 with distinct refs; missing config, missing vars, identical refs, and wrong working directory should exit 1.
