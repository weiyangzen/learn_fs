# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/inform.c

Implements a small RFC2136 DNS UPDATE client used to “inform” Windows 2003 DNS servers of the local host’s A record. It reads local NDB data, builds a DNS update packet manually, sends it over UDP, and checks the response code.

The program finds `$sysname`, opens NDB, queries `dom`, `dnsdomain`, `ns`, and `inform`, then chooses `inform` over `dom` when present. It obtains the local IPv4 address from `myipaddr()`, dials the configured DNS server, writes an update deleting the old A record and adding the current one with a 25-hour TTL.

Packet helpers `p16`, `p32`, `pmem`, and `pname` manually encode DNS fields/names. It waits up to three seconds for a response with matching transaction ID and treats response code 7 as a nonfatal “already exists” warning.

Risks include manual packet construction with no bounds checks on encoded names, IPv4-only update data, and use of low response-code mask (`& 7`) rather than full DNS extended code handling.
