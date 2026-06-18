# sources/user-network-fs/samba/source4/torture/ndr/witness.c

Purpose: This file is an NDR regression suite for the Witness protocol. It verifies captured input, output, pull-push round trips, and invalid-data handling for Witness interface list, registration, unregistration, and async notification structures.

Important APIs, types, and functions: Static fixtures cover `witness_GetInterfaceList`, `witness_Register`, `witness_UnRegister`, `witness_AsyncNotify`, and a malformed `witness_notifyResponse`. Checker functions validate `struct witness_interfaceList`, context handles, GUIDs, `struct witness_notifyResponse`, `witness_ResourceChange`, and `witness_IPaddrInfoList`. `ndr_witness_suite()` registers pull, pull-push, and invalid-data tests.

Control flow: The suite decodes the interface list output and asserts two interfaces named `NODE2` and `NODE1` with IPv4 addresses and flags. It then decodes Witness Register input and output, matching version, net name, IP address, client computer name, returned GUID context handle, and success status. UnRegister and AsyncNotify input fixtures validate context-handle decoding. AsyncNotify output fixtures validate resource-change and client-move message branches, including a fuzz case with zero addresses. The final invalid-data fixture expects `NDR_ERR_BAD_SWITCH`.

State and persistence behavior: No server state is mutated. The file uses captured byte streams and transient decoded structures only.

Dependencies and integration points: It depends on the generated Witness NDR bindings, Samba's NDR torture framework, GUID parsing, WERROR assertions, and protocol constants such as `WITNESS_NOTIFY_RESOURCE_CHANGE`, `WITNESS_NOTIFY_CLIENT_MOVE`, and `WITNESS_IPADDR_V4`.

Risks: The tests are exact binary compatibility checks, so alignment, union discriminator, conformant-array, string, GUID, IPv4, and IPv6 formatting changes can break them. The file also encodes selected fuzz expectations; parser hardening can regress if the bad-switch fixture starts being accepted.

Test signals: Passing results show that Witness NDR pull, selected pull-push reserialization, context handles, nested notify unions, IP address decoding, and invalid union-switch rejection remain stable.
