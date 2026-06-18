<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/redhat/main.yml

Purpose: installs pynfs build/runtime dependencies on redhat family systems.

Important APIs/types/functions: modules `ansible.builtin.include_role`, `ansible.builtin.dnf`, `ansible.builtin.pip`; variables/facts `become_method`, `update_cache`, `retries`, `delay`, `until`, `packages`; tasks `Enable the CodeReady repo`, `Install build dependencies for pynfs`, `Install xdrlib3`.

Control flow: Uses the distro package manager with package lists needed for git, Python tooling, NFS utilities, and Kerberos/RPC support as defined in the task.

State and persistence behavior: Mutates package state only.

Dependencies and integration points: Included by `pynfs/tasks/install-deps/main.yml`.

Risks: Package names and Python version assumptions differ by distribution; missing deps surface later during `setup.py build` or test scripts.

Test signals: Signals are idempotent install and successful subsequent pynfs build.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/redhat/main.yml -->
