# sources/test-tools/syzkaller/pkg/declextract/netlink.go

Purpose: `netlink.go` serializes extracted generic-netlink families, operations, and attribute policies into syzkaller descriptions and interface metadata.

Important APIs/types/functions: `serializeNetlink` emits family resources, message header aliases, `syz_genetlink_get_family_id` calls, sendmsg calls for operations, and associated `NETLINK` interfaces. `policyQueue` ensures policies are emitted lazily on first use. `serializeNetlinkPolicy`, `nlattrType`, `netlinkType`, and `netlinkTypeInt` lower netlink attribute schemas into syzlang types.

Control flow and state: all extracted policies are loaded into `policyQueue`. Each family with operations gets a generated family id resource and message type. Operation policies are marked used; pending policies are drained after each family. Nested attributes recursively enqueue nested policies. Binary attributes are converted to scalar, buffer, struct, or array types based on explicit element type and maximum size.

Dependencies and integration: this file uses `stringIdentifier`, `fieldType`, `ctx.structs`, and `ctx.error` from the main declextract context. `Interface` records connect netlink operations back to source file, function, access level, and identifying command.

Risks: families without operations are skipped with a TODO, so broadcast-only APIs are not described. Unknown netlink integer kinds panic. Binary attributes with missing structs or odd element sizes accumulate errors. Policy naming assumes extracted names are unique after `$auto` suffixing. No direct tests are included.
