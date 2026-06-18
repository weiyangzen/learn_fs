# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/install-deps/debian/main.yml

Purpose: Debian-family package installation for sysbench workflows.

Important APIs/types/functions: uses optional `include_vars`, `apt update_cache`, and multiple `apt` package lists for Docker/MySQL, PostgreSQL build/runtime, sysbench, and Python plotting packages.

Control flow: loads optional extra vars, refreshes apt metadata, installs common Docker/sysbench dependencies when MySQL Docker mode is enabled, and installs PostgreSQL build/runtime/sysbench/plotting dependencies when PostgreSQL native mode is enabled.

State/persistence behavior: mutates system package state and apt cache. It does not create benchmark data directly.

Dependencies/integration: selected by `install-deps/main.yml` when `ansible_facts.os_family` is Debian. Depends on `sysbench_type_mysql_docker` and `sysbench_type_postgresql_native`.

Risks/test signals: package names are distro-version sensitive, especially PostgreSQL build libraries and Docker packages. Test signals are successful apt completion and later ability to build PostgreSQL, run Docker, run sysbench, and import plotting libraries.
