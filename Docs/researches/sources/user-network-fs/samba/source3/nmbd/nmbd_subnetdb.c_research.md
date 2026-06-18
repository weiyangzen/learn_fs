# sources/user-network-fs/samba/source3/nmbd/nmbd_subnetdb.c

## Purpose
`nmbd_subnetdb.c` constructs and manages nmbd's subnet database. It opens IPv4 UDP sockets for normal broadcast subnets, creates special unicast, remote-broadcast, and WINS-server subnet records, and provides subnet iteration helpers.

## Important APIs, types, and functions
- Global subnet roots: `subnetlist`, `unicast_subnet`, `remote_broadcast_subnet`, `wins_server_subnet`.
- `make_normal_subnet` creates socket-backed normal subnets.
- `create_subnets` waits for IPv4 interfaces, creates normal subnets, then creates special subnets.
- `close_subnet` closes sockets and removes a subnet without freeing it.
- `we_are_a_wins_client` and `get_next_subnet_*` guide special-subnet iteration.

## Control flow
Startup calls `create_subnets`, which waits for IPv4 non-loopback interfaces, filters interface records, opens NMB/DGRAM sockets for normal subnets, and then creates socketless unicast/remote-broadcast/WINS-server special subnets. WINS-server mode uses the first IPv4 interface address as the unicast address.

## State and persistence behavior
The module owns process-global subnet records and socket descriptors. It persists nothing to disk. Subnet records hold mutable child state owned by other modules, including name lists, workgroup lists, response lists, and change flags.

## Dependencies and integration points
Dependencies include interface discovery/loading, socket helpers, loadparm WINS/broadcast settings, `global_nmb_port`, and linked-list macros. Consumers include packet listening/routing, name registration, WINS, and browser database code.

## Risks and edge cases
nmbd is IPv4-only here and waits if no IPv4 non-loopback interface exists. Socket creation failure aborts startup. Special subnets are outside `subnetlist`, so callers must use the right iteration helper. `close_subnet` avoids dangling references but leaks until exit.

## Test signals
Test multi-interface startup, loopback-only systems, bind-interface-only modes, explicit broadcast binding, WINS server/client combinations, and subnet iteration inclusion rules.
