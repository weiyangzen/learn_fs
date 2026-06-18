# sources/security-integrity/selinux/libsepol/src/node_internal.h

## Purpose
Private include bridge for node record and node database APIs. It gives implementation files a single local header that includes the public high-level node record declarations and node policydb operation declarations.

## Important APIs, Types, and Functions
No new functions or types are declared here. It exposes whatever is provided by `<sepol/node_record.h>` and `<sepol/nodes.h>` to local implementation files such as `node_record.c` and `nodes.c`.

## Control Flow
There is no runtime control flow. The include guard `_SEPOL_NODE_INTERNAL_H_` prevents duplicate inclusion.

## State and Persistence Behavior
No runtime state or persistence. The file only affects compilation and dependency visibility.

## Dependencies and Integration Points
Integrates the record-level API (`sepol_node_t`, `sepol_node_key_t`) with policydb CRUD operations for node contexts. This local header keeps source files coupled to both public surfaces without repeating includes.

## Risks and Edge Cases
The header is intentionally minimal; any private helper prototypes added later would widen the internal ABI. Current risk is low, limited to include-order or missing-declaration problems if public headers change.

## Test Signals
Compilation of `node_record.c` and `nodes.c` is the main signal. Include hygiene tests should catch missing public declarations or circular include changes.
