# sources/security-integrity/selinux/.github/workflows/tf_testsuite.yml

Purpose: schedules SELinux testsuite runs in Testing Farm.

Important jobs/steps: triggers on push and pull_request, matrixes `x86_64` and `aarch64`, and invokes `sclorg/testing-farm-as-github-action@main` with `TESTING_FARM_API_TOKEN` and selected architecture.

Control flow: single scheduling step per architecture. The actual test plan is delegated to Testing Farm configuration outside this file.

State and dependencies: depends on repository secret, external action at `main`, and Testing Farm service availability.

Risks and test signals: mutable action reference and secret availability can disable signal. It broadens architecture coverage beyond GitHub-hosted x86_64 runners.
