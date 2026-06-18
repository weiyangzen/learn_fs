# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/inform.c

Builds and sends RFC2136 DNS UPDATE messages for Windows DNS-style “inform” updates.

Key elements:
- Reads local `sysname` and ndb attributes `dom`, `dnsdomain`, `ns`, and `inform`.
- Converts domain names to IDN wire names with `utf2idn`.
- Constructs a DNS UPDATE packet manually with zone, delete-old-A/AAAA records, and add-new A/AAAA records.
- Enumerates local interfaces with `readipifc`, skipping unspecified and loopback addresses.
- Sends the update to the configured DNS server over UDP.
- Waits up to 3 seconds for a matching transaction ID and maps response codes to human-readable errors.

Notable behavior:
- Uses opcode `5<<11` for DNS UPDATE.
- TTL for added address records is 25 hours.
- Error code 7 is treated as a warning/acceptable “RR exists” case.

Risks and quirks:
- Manual packet construction bypasses shared DNS message conversion.
- `err = g16(&p) & 7` only inspects low three bits, not the full DNS RCODE.
