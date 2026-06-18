# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/json.c

JSON configuration and topology serialization for libnvme hosts, subsystems, controllers, namespaces, and fabrics options.

Key behavior:
- Parses a strict JSON array config into existing/created libnvme host/subsystem/controller objects.
- Reads host fields such as `hostnqn`, `hostid`, `dhchap_key`, `hostsymname`, and persistent discovery controller state.
- Reads subsystem fields including `nqn`, `application`, and `ports`.
- Updates fabrics controller config fields such as queue counts, timeouts, digest flags, TLS settings, keyring, TLS key identity, and persistent/discovery flags.
- Writes persistent config back as a JSON array, skipping PCIe controllers and discovery subsystems where appropriate.
- Dumps runtime tree state as a JSON object containing hosts, subsystems, namespaces, paths, ANA state, NUMA nodes, queue depth, and controller details.

Important dependencies:
- json-c APIs: `json_object_*`, `json_tokener_*`, `json_object_to_fd`.
- libnvme tree accessors and mutators from `libnvme.h`.
- Internal logging through `libnvme_msg()`.

Research notes:
- Parsing updates only unset/default-ish controller config fields for many options, preserving values already set elsewhere.
- Config update and tree dump are separate views: config output targets reconnect/fabrics persistence, while tree dump targets discovered runtime topology.
- Strict JSON parsing is enforced through `JSON_TOKENER_STRICT`.
