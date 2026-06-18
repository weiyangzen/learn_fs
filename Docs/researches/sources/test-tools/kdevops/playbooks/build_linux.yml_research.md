# sources/test-tools/kdevops/playbooks/build_linux.yml

Purpose: runs the build-linux workflow repeatedly on baseline/dev systems with optional monitoring around the build phase.

Important APIs/types/functions: targets `baseline:dev`, imports `roles/bootlinux/tasks/install-deps/main.yml`, optionally imports monitoring install/run/collect task files based on `enable_monitoring`, and applies role `build_linux`.

Control flow: install kernel-build dependencies, install and start monitors if enabled, execute the build role, then collect monitoring data.

State/persistence behavior: creates build trees, compiler artifacts, result files, and optional monitoring outputs. Monitoring state is started before the role and collected afterward.

Dependencies/integration: depends on bootlinux tasks, monitoring tasks, build-linux role variables, and baseline/dev inventory.

Risks/test signals: monitor startup/collection must bracket the build accurately or data will be misleading. Test signals are successful build result files, monitoring artifacts when enabled, and no lingering monitor processes.
