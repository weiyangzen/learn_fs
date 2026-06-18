# sources/test-tools/stress-ng/core-net.h

Purpose: defines networking constants and helper declarations shared by socket-based stressors.

Important APIs/types: domain masks, address selectors, port ranges, default stressor port bases, and declarations for domain, sockaddr, reservation, release, checksum, and wraparound helpers.

Control flow: no runtime flow. Constants encode the stress-ng high-port allocation convention beginning at 49152.

State/persistence: no state in the header; reservation APIs affect shared runtime port allocation state in `core-net.c`.

Dependencies/integration: includes `<sys/socket.h>` and `core-attribute.h`, and relies on `stress_args_t` from the common include chain.

Risks: default port offsets must remain non-overlapping and within range; adding a network stressor requires coordinated option IDs and port defaults.

Test signals: compile socket stressors, verify default port constants stay within range, and test `WARN_UNUSED` callers.
