# File Research: sources/os/bsd/openbsd-src/sbin/iked/radius.c

This file implements OpenIKED RADIUS integration for EAP authentication, Configuration Payload attribute mapping, accounting, retry/failover, and Dynamic Authorization Extensions disconnect handling.

Key responsibilities:
- Defines default RADIUS-to-IKEv2 CP mappings for IPv4 address, netmask, DNS, and NBNS attributes, including Microsoft vendor attributes.
- `iked_radius_request` converts EAP Response messages into RADIUS Access-Request packets, stores request state, includes User-Name, State, EAP-Message, NAS attributes, and schedules send/retry.
- `iked_radius_on_event` receives RADIUS responses, matches by ID, validates authenticators, processes Access-Challenge/Accept/Reject, extracts EAP MSK, updates protected User-Name/class attributes, advances SA auth state, maps CP attributes, and forwards EAP payloads back into IKE_AUTH.
- `iked_radius_request_send` performs server selection, retry backoff, request ID allocation, failover, NAS-IP/NAS-Identifier insertion, accounting delay calculation, authenticator generation, packet send, and timer rescheduling.
- `iked_radius_config` maps configured or default RADIUS attributes into SA/request Configuration Payload reply data.
- Accounting helpers send Accounting-On/Off, Start, Stop, and interim-style records through `iked_radius_acct_request`.
- `iked_radius_dae_on_event` implements Disconnect-Request handling from authorized DAE clients, with lookup by Acct-Session-Id, User-Name, or Framed-IP-Address, and emits ACK/NAK/CoA-NAK responses.

Important dependencies:
- Uses OpenBSD `radius(3)` packet APIs, libevent timers, OpenIKED `ibuf`, SA state management, and IKEv2 EAP send/delete helpers.
- Uses the shared timer helper from `timer.c`.

Security and correctness notes:
- Validates response authenticators and message authenticators before trusting authentication responses.
- Keeps RADIUS State pinned to a server; failover is refused once State exists.
- Accounting falls back to IKE ID when authenticated EAP identity is absent, but RFC guidance is noted in comments.
- DAE requests are accepted only from configured clients and authenticated with the client secret.
- Notable implementation quirk: the IPv6 CP mapping branch sets `addr->addr_af = AF_INET` before filling an IPv6 sockaddr; this looks inconsistent with the surrounding IPv6 handling and is worth reviewing against upstream history.
