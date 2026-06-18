# sources/test-tools/liburing/test/napi-test.sh

Purpose: creates an isolated two-namespace veth topology and runs `napi-test.t` sender/receiver pairs for multiple queue flag configurations.

Important APIs/types/functions: `ip netns`, `ip link add ... type veth`, `ethtool -K`, shell `trap`, `QUEUE_FLAGS="0x0 0x3000 0x2"`, and executable discovery for `napi-test.t`.

Control flow: verifies `ip` and `ethtool` exist, installs an EXIT cleanup trap, creates client/server namespaces and veth peers, assigns `10.10.10.10/24` and `10.10.10.20/24`, adjusts offloads, brings links up, then for each flag starts receiver in server namespace, runs sender in client namespace, and waits.

State and persistence behavior: creates temporary network namespaces and veth devices, deleted by `clean_namespaces` on exit. No repository files are modified.

Dependencies and integration points: requires root or namespace privileges, iproute2, ethtool, and the compiled test binary in current or `test/` path.

Risks and test signals: missing tools exit 77, missing binary exits 77, and networking/setup failures propagate as nonzero shell exits. Cleanup assumes namespace names are not used by other processes.
