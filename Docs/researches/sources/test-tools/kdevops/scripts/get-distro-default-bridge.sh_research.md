<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-default-bridge.sh -->
# sources/test-tools/kdevops/scripts/get-distro-default-bridge.sh

Purpose: returns the default bridge IP address for a distro and virtualization type. Today it always returns `192.168.122.1`.

Important APIs and functions: no functions. It reads `$1` as `DISTRO`, `$2` as `VIRT_TYPE`, calls `scripts/os-release-check.sh fedora`, and echoes the default bridge.

Control flow: assigns arguments, runs a Fedora detection command, echoes `192.168.122.1` and exits whether Fedora is detected or not.

State and persistence: no persistent state; reads host os-release indirectly through `os-release-check.sh`.

Dependencies and integration: bash and `scripts/os-release-check.sh`. `scripts/provision.Makefile` exports `KDEVOPS_DEFAULT_BRIDGE_IP_GUESTFS` from this script.

Risks: parameters are currently unused, so the interface promises distro/virt-specific behavior that is not implemented. Running from outside the repo root can break the relative `scripts/os-release-check.sh` call. Test signals are straightforward: run for supported distro names and assert the default IP, plus test from non-root cwd if callers rely on it.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get-distro-default-bridge.sh -->
