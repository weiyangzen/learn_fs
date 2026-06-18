<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/systemd/nfs-ganesha-config.service-in.cmake -->
# sources/user-network-fs/nfs-ganesha/src/scripts/systemd/nfs-ganesha-config.service-in.cmake

## Purpose
This CMake-templated systemd unit defines a oneshot service for processing NFS-Ganesha configuration before or during service startup.

## Important APIs, Types, and Functions
The unit has `[Unit]` metadata with `Description=Process NFS-Ganesha configuration` and `DefaultDependencies=no`. The `[Service]` section sets `Type=oneshot` and runs `@LIBEXECDIR@/ganesha/nfs-ganesha-config.sh`, where `@LIBEXECDIR@` is substituted by CMake at install/configuration time.

## Control Flow
Systemd starts the unit, runs the config helper once, and treats the service as complete when the script exits. This file does not define ordering dependencies itself; those are expected to be supplied by packaging or other unit relationships.

## State and Persistence Behavior
The unit itself stores no state. The invoked `nfs-ganesha-config.sh` may generate or validate runtime configuration depending on package layout. Systemd records normal service status and logs.

## Dependencies and Integration Points
It depends on systemd and the installed helper script in the configured libexec directory. It integrates with CMake packaging and the broader `nfs-ganesha.service` unit set.

## Risks and Test Signals
Risks include incorrect CMake substitution, missing executable install permissions, and insufficient ordering because `DefaultDependencies=no` removes standard unit dependencies. Test signals are package install checks, `systemd-analyze verify`, `systemctl start nfs-ganesha-config.service`, and startup behavior when the helper exits nonzero.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/systemd/nfs-ganesha-config.service-in.cmake -->
