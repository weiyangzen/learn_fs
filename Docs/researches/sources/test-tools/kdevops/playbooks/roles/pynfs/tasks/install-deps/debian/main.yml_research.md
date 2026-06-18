<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/debian/main.yml

Purpose: installs pynfs build/runtime dependencies on debian family systems.

Important APIs/types/functions: modules `ansible.builtin.apt`; variables/facts `become_method`, `update_cache`; tasks `Install pynfs build dependencies`, `Install xdrlib from Debian package on Debian 13+`.

Control flow: Uses the distro package manager with package lists needed for git, Python tooling, NFS utilities, and Kerberos/RPC support as defined in the task.

State and persistence behavior: Mutates package state only.

Dependencies and integration points: Included by `pynfs/tasks/install-deps/main.yml`.

Risks: Package names and Python version assumptions differ by distribution; missing deps surface later during `setup.py build` or test scripts.

Test signals: Signals are idempotent install and successful subsequent pynfs build.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/debian/main.yml -->
