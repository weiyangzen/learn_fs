# File Research: sources/os/bsd/openbsd-src/sbin/iked/config.c

`config.c` manages runtime object allocation, teardown, and configuration IPC. It creates and frees IKE SAs, policies, proposals, transforms, flows, Child SAs, users, sockets, PF_KEY state, keys, static daemon settings, OCSP settings, and RADIUS-related configuration.

SA cleanup in `config_free_sa()` is broad: timers, fragments, proposals, Child SAs, interface configuration, flows, RADIUS accounting, address pools, policy refs, retransmit queues, nonces, DH material, crypto state, AUTH/cert/EAP buffers, configuration payloads, tags, RADIUS requests, and counters. Policy cleanup handles refcounted policy removal when SAs still point at a policy.

Configuration data is serialized through imsg. Policies are sent as a policy header plus proposal/transform records; flows are sent separately. Keys are read from `IKED_PRIVKEY`, serialized through CA helper functions, and sent to the CA process as private and public key imsgs.

Reset handling supports policy, SA, user, RADIUS, CA, and all-state resets. Socket/PF_KEY helpers bind privileged resources in the parent and pass file descriptors to the IKEv2 process. RADIUS helpers configure auth/accounting servers, config maps, DAE listeners, and DAE clients.

Security-relevant details: private key imsg data is explicitly zeroed after receipt, RADIUS secrets use variable-length trailing storage, no-action mode prints/parses without installing runtime config, and reset paths carefully close sockets/events and free outstanding RADIUS requests.
