# sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/yaml-config.go

Purpose: writes YAML configuration files into the current integration test directory.

Important APIs/types/functions: `YAMLConfigFile(yamlContent any, fileName string) string`.

Control flow: marshals arbitrary content with `yaml.Marshal`, joins the target name under `TestDir()`, writes the file with mode `0644`, and exits the process through `LogAndExit` on marshal or write failure.

State/persistence behavior: persists config files inside the integration test temp directory, often for generated gcsfuse mount config flags.

Dependencies/integration: used by setup helpers such as HNS flag injection and tests that need config files at runtime.

Risks/test signals: fatal process exit on write failures prevents local test recovery. It assumes `TestDir()` has already been initialized.
