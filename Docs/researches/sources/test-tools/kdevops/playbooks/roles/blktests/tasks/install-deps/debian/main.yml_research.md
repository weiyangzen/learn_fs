# sources/test-tools/kdevops/playbooks/roles/blktests/tasks/install-deps/debian/main.yml

This Debian-specific dependency file updates apt metadata, installs `nvme-cli`, and installs the packages needed to build and run blktests, blktrace, NBD, dbench, filesystem tools, multipath tools, fio, compilers, headers, and development libraries.

Important APIs are `ansible.builtin.apt` with `become`. Control flow is linear package installation. Persistent state is the system package database and installed tools. Integration points are the main blktests role, Debian/Ubuntu package names, and variables such as `pkg_libaio`. Risks include duplicate package entries, missing variable `pkg_libaio`, package-name drift between Debian releases, and broad dependency installation on test hosts. Test signals should run apt check mode or molecule-style provisioning on supported Debian releases and verify tools such as `nvme`, `fio`, and compiler commands exist.
