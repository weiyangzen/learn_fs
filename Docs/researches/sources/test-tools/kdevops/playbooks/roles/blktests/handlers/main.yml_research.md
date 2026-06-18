# sources/test-tools/kdevops/playbooks/roles/blktests/handlers/main.yml

This handler restarts the watchdog daemon using the service name stored in `watchdog_service_name`. It is a single Ansible service action named `Restart watchdog daemon`.

The important API is `ansible.builtin.service` with `state: restarted`. Control flow is event-driven: the handler runs only when notified by other tasks or roles. Persistent state is limited to the system service lifecycle. Integration depends on watchdog configuration elsewhere in the kdevops playbooks and on `watchdog_service_name` being defined for the target distribution. Risks are simple but operationally important: an undefined or wrong service name will fail handler execution, and restarting watchdog during long block tests may affect failure detection timing. Test signals should include handler notification in a host with a known watchdog service and an undefined-variable lint check.
