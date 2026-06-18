# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/dotest

Tiny rc helper for PPP test setup.

Behavior:
- Ensures `/net.alt/tcp` and `/net.alt2/tcp` are bound from `#I1` and `#I2`.
- Kills old `8.out` and `testppp` processes if present.
- Runs `testppp`.

Integration points:
- Intended local test harness helper for the PPP implementation.
