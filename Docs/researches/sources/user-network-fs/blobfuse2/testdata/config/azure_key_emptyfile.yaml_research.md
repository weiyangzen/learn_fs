<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_emptyfile.yaml -->
# sources/user-network-fs/blobfuse2/testdata/config/azure_key_emptyfile.yaml

Source path: `sources/user-network-fs/blobfuse2/testdata/config/azure_key_emptyfile.yaml`

## Purpose
Blobfuse2 test configuration selecting `file cache` behavior with auth mode/template `key/SAS/MSI/SPN/CLI placeholder values`.

## Important APIs, Types, And Functions
Top-level/config keys: `logging`, `level`, `file-path`, `type`, `components`, `libfuse`, `attribute-expiration-sec`, `entry-expiration-sec`, `negative-entry-expiration-sec`, `ignore-open-flags`, `file_cache`, `path`, `timeout-sec`, `max-size-mb`, `allow-non-empty-temp`, `cleanup-on-start`, `create-empty-file`, `attr_cache`, plus 10 more. Pipeline components: `libfuse`, `file_cache`, `attr_cache`, `azstorage`. Authentication/config mode: `{ STO_ACC_TYPE }`.

## Control Flow
The config is consumed by `blobfuse2 mount --config-file` or test harness templating. Component order builds a libfuse-to-cache/stream/xload-to-attr-cache-to-azstorage or loopback pipeline, and placeholder tokens such as `{ 0 }` and `{ 1 }` are substituted by test tooling for container and cache paths.

## State And Persistence
The file itself is static testdata. At runtime it directs blobfuse2 to create log files, local cache directories, mounted Azure or loopback filesystem state, and optional health-monitor output.

## Dependencies And Integration Points
Integrates with blobfuse2 configuration parsing, Azure Storage credentials supplied by environment/template replacement, local cache paths, logging, health-monitor settings where present, and scenario/performance scripts that pass these files to mount commands.

## Risks
Template placeholders must be populated with valid secrets, account names, endpoints, and paths before use. Misordered or incompatible components can fail mount initialization. Special behavior: changes empty-file creation behavior.

## Test Signals
Signals are successful mount initialization with this config, expected cache/log/health-monitor side effects, and scenario tests demonstrating the targeted mode such as block cache, direct I/O, proxy, symlink, streaming, xload, or auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/config/azure_key_emptyfile.yaml -->
