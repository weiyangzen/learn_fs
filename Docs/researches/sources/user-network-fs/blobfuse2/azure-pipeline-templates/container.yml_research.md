# sources/user-network-fs/blobfuse2/azure-pipeline-templates/container.yml

## Purpose
This template manages temporary Azure Storage containers and ADLS container SAS values for pipeline tests.

## Important APIs, Types, and Functions
Parameters switch among `generate_container`, `create_container`, `delete_container`, and `generate_adls_sas`, with account metadata and optional container name. It uses Azure CLI `az storage container create/delete` and `az storage fs generate-sas`.

## Control Flow
When generating a container, it creates a random 40-character lowercase/number name and sets Azure DevOps variable `containerName`. When creating, it uses account key auth and `--fail-on-exist`. When generating ADLS SAS, it creates a 70-minute filesystem SAS with broad ACL/data permissions and stores it as `BF2_ADLS_ACC_SAS`. When deleting, it deletes `$(containerName)` from the specified account.

## State and Persistence Behavior
Persistent state is storage containers in Azure accounts and pipeline variables set through `##vso[task.setvariable]`. Steps run only when `variables['distro'] == 'ubuntu'`.

## Dependencies and Integration Points
It is used by `build.yml`, `cleanup.yml`, and release/unit-test setup. It depends on Azure CLI, account names/keys, and a valid distro variable.

## Risks and Edge Cases
Non-Ubuntu jobs skip creation/deletion because of conditions, so callers must provide existing containers or handle cleanup differently. The random-name generation can block or be slow on entropy-starved hosts. SAS expiry is short and can expire in long jobs.

## Test Signals
Signals include visible `containerName` variable, successful container creation in both accounts, generated ADLS SAS, and cleanup deleting the same container.
