# sources/user-network-fs/blobfuse2/azure-pipeline-templates/build.yml

## Purpose
This is the central Azure DevOps setup template: it installs distro dependencies, checks out/builds Blobfuse2, creates mount/cache/GOPATH directories, creates temporary Azure containers, generates ADLS SAS, writes Azure test configuration, and optionally runs unit tests.

## Important APIs, Types, and Functions
Parameters control MSI/AzCLI skipping, health monitor build, proxy setup, and unit test execution. It composes `package-install.yml` and `container.yml`, calls `go_installer.sh`, `Go@0 get/test/tool`, `./build.sh $(tags)`, `./build.sh health`, `blobfuse2 --version`, and writes `$HOME/azuretest.json`.

## Control Flow
The template installs packages for the current `distro`, checks out self, prints environment and disk info, optionally installs and configures mitmproxy, installs Go, downloads dependencies, builds Blobfuse2 and optionally `bfusemon`, verifies the binary, prepares mount/cache/GOPATH directories, generates a random container name, creates block and ADLS containers, generates ADLS container SAS, writes test credentials/config flags to `$HOME/azuretest.json`, optionally runs unit tests and coverage report, and saves `utcover.cov`.

## State and Persistence Behavior
State includes generated containers in Azure storage, SAS variables set through `##vso[task.setvariable]`, local mount/cache directories, Go workspace, built binaries, optional coverage artifacts, and `$HOME/azuretest.json`. Container cleanup is left to calling pipelines via `cleanup.yml`.

## Dependencies and Integration Points
Nearly every Azure pipeline stage invokes this template. It depends on variable group `NightlyBlobFuse`, distro matrix variables, package install support, Azure CLI, storage account secrets, and repository test code.

## Risks and Edge Cases
Secrets are written into a JSON file and printed. Unit test step is `continueOnError: true` in this template, so callers must check coverage/report implications. Proxy setup exports environment variables in one shell step only, which may not affect later steps. Container creation is conditional on Ubuntu inside `container.yml`, which matters for non-Ubuntu stages.

## Test Signals
Signals include package install success, `blobfuse2 --version`, created storage containers, generated ADLS SAS, valid `$HOME/azuretest.json`, unit test and coverage output when enabled, and later cleanup deleting containers.
