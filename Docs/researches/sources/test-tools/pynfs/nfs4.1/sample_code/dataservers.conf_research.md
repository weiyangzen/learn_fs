# sources/test-tools/pynfs/nfs4.1/sample_code/dataservers.conf

## Purpose
`dataservers.conf` is a sample configuration file for files-layout pNFS data servers. It shows the address grammar expected by pynfs sample code and documents how file striping order follows listed data servers.

## Important APIs, Types, and Functions
This is a configuration sample, not executable code. Supported line forms are documented as `server[:[port][/path]]` and multipath addresses as comma-separated server entries followed by an optional `/path`.

## Control Flow
Consumers read the file line by line to discover data-server addresses, optional ports, and optional paths. The examples cover IPv4, bracketed IPv6, and mixed multipath forms.

## State and Persistence Behavior
The file itself is static sample state. Runtime server state is created by whichever parser consumes these entries and connects data servers to an MDS/files layout.

## Dependencies and Integration Points
The server CLI in `nfs4server.py` has a `--dataservers` option defaulting to `dataservers.conf`. Files-layout sample exports and data-server code use this style of file to build pNFS DS topology.

## Risks and Edge Cases
It contains hard-coded example IP addresses and paths that are unlikely to work without local editing. IPv6 requires brackets to avoid ambiguity with port parsing. Comments say files stripe in listed order, so parser ordering matters.

## Test Signals
Useful test signals are parser acceptance of IPv4, IPv6, and multipath lines; defaulting of missing port to 2049; defaulting of missing path to `/`; and correct preservation of DS ordering.
