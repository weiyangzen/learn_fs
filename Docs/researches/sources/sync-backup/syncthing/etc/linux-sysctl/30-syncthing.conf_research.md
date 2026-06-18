# sources/sync-backup/syncthing/etc/linux-sysctl/30-syncthing.conf

## Purpose
This sysctl configuration raises Linux maximum socket receive and send buffer sizes to support better QUIC performance. It is a deployment tuning file, not Syncthing application logic.

## Important APIs, Types, And Functions
The file sets `net.core.rmem_max = 7340032` and `net.core.wmem_max = 7340032`, with a comment linking the rationale to QUIC UDP buffer-size guidance. The value is 7 MiB.

## Control Flow
There is no executable flow. Linux sysctl tooling reads the file, usually from `/etc/sysctl.d/`, and applies the kernel parameters at boot or when `sysctl --system` is run.

## State And Persistence Behavior
The file persists desired kernel networking defaults. Applied values change kernel runtime state until reboot or later sysctl changes; installation in sysctl.d makes them reapply across boots.

## Dependencies And Integration Points
It integrates with Linux kernel networking and QUIC libraries used by Syncthing's transport stack. Larger UDP buffers reduce packet loss risk for high-throughput QUIC connections. It is distribution/package integration material.

## Risks And Edge Cases
Raising global max buffer sizes affects the whole system, not only Syncthing. Administrators may reject package-installed sysctl changes or need different values for constrained systems. The file sets maxima, not per-socket buffers directly; application/socket behavior still determines actual allocation.

## Test Signals
Validation consists of applying the sysctl config and checking `sysctl net.core.rmem_max net.core.wmem_max`. Performance testing should look for reduced QUIC buffer warnings and improved transfer stability on high-throughput links.
