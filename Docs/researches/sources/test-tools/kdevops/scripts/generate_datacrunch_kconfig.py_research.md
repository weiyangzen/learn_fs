<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_datacrunch_kconfig.py -->
# sources/test-tools/kdevops/scripts/generate_datacrunch_kconfig.py

Purpose: generates DataCrunch dynamic Kconfig files for instance types, OS images, and locations, using live DataCrunch API data when credentials and connectivity are available and static fallback defaults otherwise.

Important APIs and functions: `sanitize_kconfig_name()` uppercases and replaces Kconfig-unsafe characters; `generate_instance_types_kconfig()` filters H100/GPU instance types and emits choice plus string value config; `generate_images_kconfig()` prefers PyTorch then Ubuntu images; `generate_locations_kconfig()` emits datacenter choices; `main()` writes selected generated files under `terraform/datacrunch/kconfigs` by default.

Control flow: parse `--output-dir` and `--type`, warn if no API key/client secret is available, ensure output directory, generate each requested Kconfig string, and write `Kconfig.compute.generated`, `Kconfig.images.generated`, and/or `Kconfig.location.generated`.

State and persistence: writes generated Kconfig files directly. It reads credentials indirectly through `datacrunch_api.py`.

Dependencies and integration: imports DataCrunch API helpers. `generate_cloud_configs.py` and `scripts/dynamic-cloud-kconfig.Makefile` invoke it; generated files are sourced by DataCrunch Kconfig fragments.

Risks: price conversion uses `float()` on provider data and can fail for unexpected values. Fallback instance symbol `1X_H100_PCIE` may not match live naming. It warns about missing API key but still calls list functions, which will print credential errors. Test signals include mocked API response fixtures, fallback mode, Kconfig syntax checks, and sanitization edge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_datacrunch_kconfig.py -->
