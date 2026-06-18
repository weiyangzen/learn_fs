# sources/security-integrity/selinux/libsepol/cil/src/cil_internal.h

## Purpose
`cil_internal.h` is the primary internal ABI for the CIL frontend in libsepol. It defines database state, keyword globals, symbol-table indices, AST payload structs for CIL declarations and rules, constants, and initializer/destructor/function prototypes shared across implementation files.

## Important APIs, Types, And Functions
Important global structures include `struct cil_db`, `struct cil_root`, `struct cil_sort`, `struct cil_ordered`, and payload structs such as `cil_block`, `cil_class`, `cil_perm`, `cil_type`, `cil_typeattribute`, `cil_role`, `cil_user`, `cil_avrule`, `cil_deny_rule`, `cil_type_rule`, `cil_context`, file/network context structs, constraints, macros, calls, defaults, and source-info records.

The header also declares the pass enum, symbol-table index enums, keyword pointers such as `CIL_KEY_SELF`, `CIL_KEY_NOTSELF`, `CIL_KEY_ALLOW`, `CIL_KEY_DENY_RULE`, constants for AV rule kinds and attribute-use flags, and many `*_init` constructors.

## Control Flow
There is no executable flow, but the structures encode the pipeline. Parse and build phases populate raw and AST trees; post-processing fills counters, value arrays, bitmaps, sort arrays, and default policy options; binary and textual emitters consume the resolved database.

## State And Persistence Behavior
`struct cil_db` owns the main mutable compiler state: parse tree, AST, built-in pseudo-types, ordering lists, sorted context arrays, declared strings, value-to-object maps, counters, policy options, and target settings. Many payload structs store both original strings and resolved pointers. Persistence is indirect: this state is later serialized to policydb or textual policy.

## Dependencies And Integration Points
The header imports sepol policydb/service types, public `cil/cil.h`, CIL flavor/tree/symtab/memory headers, and system networking types. It is included almost everywhere in the CIL implementation, making changes high impact.

## Risks And Edge Cases
Because this header is broad, field changes can break ownership, destruction, post-processing, and emitters. Several fields are overloaded as either concrete objects, aliases, or attributes; consumers must inspect node flavor before casting. Numeric values in `enum cil_default_object`, `enum cil_default_object_range`, and fsuse types are intentionally kept equal to policydb constants.

## Test Signals
Full pipeline tests are the useful signal: parse CIL, build AST, run post-processing, emit binary/text policy, and destroy the database under sanitizers. Tests should include aliases, attributes, MLS, default rules, contexts, macros, conditionals, and target-platform-specific context rules.
