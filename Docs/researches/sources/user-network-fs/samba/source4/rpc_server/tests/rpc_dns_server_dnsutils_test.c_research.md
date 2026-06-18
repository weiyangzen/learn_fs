# sources/user-network-fs/samba/source4/rpc_server/tests/rpc_dns_server_dnsutils_test.c

## Purpose

This is a cmocka unit test file for `source4/rpc_server/dnsserver/dnsutils.c`. It verifies that `dnsserver_init_zoneinfo()` correctly initializes DNS zone info server-address arrays from zone properties for master servers and scavenging servers, including empty-property handling and deep-copy behavior.

## Important APIs, Types, And Functions

The file directly includes `../dnsserver/dnsutils.c`, so the tests exercise the implementation without a separate library boundary. Test cases are `test_dnsserver_init_zoneinfo_master_servers_empty()`, `test_dnsserver_init_zoneinfo_master_servers()`, `test_dnsserver_init_zoneinfo_scavenging_servers_empty()`, and `test_dnsserver_init_zoneinfo_scavenging_servers()`. `main()` registers those four cmocka tests and emits subunit output with `cmocka_set_message_output(CM_OUTPUT_SUBUNIT)`.

The tests construct `dnsserver_zone`, `dnsserver_serverinfo`, `dnsserver_zoneinfo`, and `dnsp_DnsProperty` objects with talloc. Property IDs under test are `DSPROPERTY_ZONE_MASTER_SERVERS` and `DSPROPERTY_ZONE_SCAVENGING_SERVERS`; populated properties use four integer IPv4 address values.

## Control Flow

Each test allocates a talloc context, creates a minimal zone named `test`, attaches one DNS property, creates an empty server-info object, calls `dnsserver_init_zoneinfo(zone, serverinfo)`, and asserts the resulting zoneinfo fields. Empty tests require the corresponding address-list wrapper to exist with count zero and NULL address array. Non-empty tests require count four, copied values, and a distinct destination array pointer; after mutating the original property array, the zoneinfo copy must retain the original values.

## State And Persistence

The tests use only transient talloc-managed memory and free it at the end of each test. There is no filesystem, network, database, or persistent server state. The important state assertion is ownership separation between input property arrays and output zoneinfo arrays.

## Dependencies And Integration Points

The file depends on cmocka, talloc, generated DNS property structures, and the internal DNS server utility implementation. In the broader build, it is an RPC server test target validating DNS server utility behavior used by the DNS RPC endpoint when reporting zone metadata.

## Risks And Edge Cases

Directly including a `.c` file couples the test to implementation-level dependencies and can miss integration issues that appear only through normal object linkage. The tests cover only one property at a time and fixed four-entry arrays; they do not cover multiple properties, allocation failure, malformed counts, NULL zone/serverinfo inputs, IPv6-like data, or other `dnsserver_init_zoneinfo()` fields. Still, the deep-copy assertions protect against dangling pointer or aliasing bugs in zoneinfo construction.

## Test Signals

The primary signal is a passing cmocka/subunit run for all four tests. Useful extensions would add multiple-property zones, larger address arrays, zero count with non-NULL source array, nonzero count with NULL source array if representable, and memory-checker runs to ensure `dnsserver_init_zoneinfo()` owns copied arrays under the expected talloc parent.
