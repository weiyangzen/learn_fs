# sources/storage-engines/rocksdb/build_tools/check-workflow-yaml.sh research

Purpose: `check-workflow-yaml.sh` validates GitHub Actions workflow YAML files before CI runtime. It catches syntax-level YAML parsing errors under `.github/workflows`.

Important APIs: the script has no arguments and exits 0 only when Ruby and the `psych` YAML library are available and every workflow `.yml` or `.yaml` parses successfully.

Control flow: `set -euo pipefail` enables strict shell behavior. The script first checks for `ruby`, then checks that Ruby can `require "psych"`. It runs an embedded Ruby program that gathers workflow files, errors if none exist, parses each file with `Psych.parse_file`, prints `OK` for valid files, records failures, and exits nonzero if any parse failed.

State and persistence: it is read-only. State is limited to the Ruby-local `bad` flag and the list of discovered workflow files.

Dependencies and integration: it depends on Bash, Ruby, and Ruby's Psych package. It is intended for developer or CI validation around GitHub Actions configuration.

Risks and test signals: this validates YAML syntax, not GitHub Actions schema semantics. It will fail on systems without Ruby even if workflows are valid. Glob behavior is limited to direct files under `.github/workflows`. Tests should cover valid YAML, malformed YAML, empty workflow directory, missing Ruby/Psych environments, and expected exit codes.
