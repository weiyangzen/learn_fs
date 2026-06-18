<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_cloud_configs.py -->
# sources/test-tools/kdevops/scripts/generate_cloud_configs.py

Purpose: orchestrates dynamic Kconfig generation for cloud providers: Lambda Labs, DataCrunch, AWS, Azure, GCE, and OCI. It also prints a concise provider summary.

Important APIs and functions: provider-specific `generate_*_kconfig()` functions run sibling/provider scripts and write generated Kconfig files; `get_lambdalabs_summary()` queries `lambda-cli` JSON endpoints; `process_*()` functions print provider status; `generate_datacrunch_kconfig()` invokes `generate_datacrunch_kconfig.py`; `main()` parses `--provider` and dispatches.

Control flow: print a heading, run one selected provider or all providers, then print menuconfig guidance. AWS/Azure/GCE/OCI each run three provider scripts and write stdout to matching generated files. Lambda and DataCrunch delegate to their own generators.

State and persistence: writes generated Kconfig files under provider `terraform/*/kconfigs` directories. No atomic writes are used, so interrupted runs can leave partial files.

Dependencies and integration: subprocesses, JSON parsing, provider-specific scripts, and Lambda CLI. It is called from `scripts/dynamic-cloud-kconfig.Makefile` for default and provider-specific cloud config targets.

Risks: executable path assumptions require running from the kdevops layout. Errors often degrade to printed warnings while leaving existing generated files untouched or partially updated. Provider script stdout is trusted as valid Kconfig. Test signals include mocking subprocesses, temp provider directories, selected-provider dispatch, write-failure paths, and invalid JSON from Lambda CLI.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_cloud_configs.py -->
