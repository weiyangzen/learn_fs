# sources/user-network-fs/samba/source3/libnet/libnet_dssync.h

## Purpose

Declares the shared DSSync context and backend callback interface for source3 libnet replication consumers.

## Important APIs, Types, and Functions

`struct dssync_ops` defines `startup`, `process_objects`, `process_links`, and `finish` callbacks. `struct dssync_context` carries domain names, RPC client, naming context DN, replication flags, object filters, bind/session data, output filename, remote DRS bind capabilities, private backend data, ops, and messages. The header declares `libnet_dssync_init_context`, `libnet_dssync`, `libnet_dssync_keytab_ops`, and `libnet_dssync_passdb_ops`.

## Control Flow

Callers initialize a context, populate required connection/options, assign an ops table, then call `libnet_dssync`. The implementation invokes backend startup before replication, object/link callbacks during each reply, and finish with the resulting UTDV.

## State and Persistence Behavior

The context is mutable and talloc-owned. It owns sensitive DRS session material and backend private pointers. Persistence is backend-defined through `private_data` and `output_filename`.

## Dependencies and Integration Points

Includes generated DRSUAPI and DRS blob types and couples backends to DRS replicated object and linked-attribute structures.

## Risks and Test Signals

Risks are caller misconfiguration and backend type assumptions for `private_data`. Tests should verify default context initialization, null optional callbacks, destructor behavior via implementation, and both external ops tables.
