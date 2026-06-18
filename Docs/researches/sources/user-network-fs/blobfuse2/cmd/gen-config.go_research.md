<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-config.go -->
# sources/user-network-fs/blobfuse2/cmd/gen-config.go

Purpose: user-facing `gen-config` command that emits a default Blobfuse2 YAML configuration for file-cache, block-cache, direct-IO, and read-only scenarios.

Important APIs/types/functions: `genConfigParams`, global `optsGenCfg`, Cobra command `generatedConfig`, `internal.GetComponent(component).GenConfig()`, `config.Set`, `common.WriteToFile`, and flags `--block-cache`, `--tmp-path`, `--direct-io`, `--o`, and `--ro`.

Control flow: if no flags are supplied the command shows help. File-cache mode requires `--tmp-path`; block-cache mode does not. It records read-only/direct-IO/tmp-path settings into config state, builds a pipeline beginning with `libfuse`, selecting `block_cache` or `file_cache`, optionally adding `attr_cache` when direct-IO is off, and ending with `azstorage`. It emits top-level direct-IO/read-only fields, logger comments, component list, each component's generated config, and commented required `azstorage` guidance. Output goes to `./blobfuse2.yaml`, a user file, or console when `--o console`.

State/persistence behavior: mutates global config state and writes/truncates a YAML file unless console output is selected. It uses absolute paths in the success message but does not validate that the cache path itself exists.

Dependencies/integration: relies on every selected component being registered in `internal` and providing stable `GenConfig()` output. It is coupled to command flag state and package-global `optsGenCfg`.

Risks/test signals: direct-IO removes `attr_cache`, and missing file-cache tmp path is intentionally an error. The custom flag error function prints help and returns nil, which may hide unknown-flag failures. Tests cover missing tmp path, file-cache and block-cache content, direct-IO content, custom output file, and console output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-config.go -->
