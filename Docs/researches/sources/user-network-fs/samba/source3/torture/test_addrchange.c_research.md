# sources/user-network-fs/samba/source3/torture/test_addrchange.c

## Purpose
`test_addrchange.c` tests Samba's local address-change notification API. It waits for network address add/delete events and prints their type and address.

## Important APIs, types, and functions
The exported test is `run_addrchange`. It uses `addrchange_context_create`, `addrchange_send`, `addrchange_recv`, `tevent_req_poll_ntstatus`, `enum addrchange_type`, and `print_sockaddr`.

## Control flow
The test creates a tevent context and addrchange context, then loops `torture_numops` times. Each iteration starts an async addrchange request, polls it to completion, receives the event type and address, maps `ADDRCHANGE_ADD`/`ADDRCHANGE_DEL` to readable strings, and prints the result.

## State and persistence behavior
No durable state is written. The test holds local event and addrchange contexts and observes OS/network-interface state changes.

## Dependencies and integration points
It is part of `smbtorture3` through `proto.h` and uses Samba's `lib/addrchange.h` API plus tevent NTSTATUS polling helpers.

## Risks and test signals
The test blocks waiting for actual address-change events, so it depends on the runtime environment. Failure to create context or receive events signals platform integration issues in the addrchange backend.
