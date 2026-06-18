# sources/user-network-fs/mergerfs/vendored/boost/describe/members.hpp

Purpose: Provides Boost.Describe member descriptor querying, including inherited member traversal and modifier filtering.

Important APIs, types, and functions: `describe_members<T,M>`, `has_describe_members<T>`, `_describe_public_members`, `_describe_protected_members`, `_describe_private_members`, `describe_inherited_members`, `member_filter`, `update_modifiers`, virtual-base tracking helpers, and hidden-name detection.

Control flow: Descriptor lists are acquired through ADL functions, appended with MP11, optionally expanded through base descriptors, and filtered by modifier flags. Inherited descriptors update access modifiers, add `mod_inherited`, and mark hidden members when derived classes declare the same name.

State and persistence behavior: Compile-time metadata only.

Dependencies and integration points: Depends on `modifiers.hpp`, `bases.hpp`, `cx_streq.hpp`, MP11 algorithm/utility/integral/list/bind, and type traits. Used by ContainerHash described-class hashing.

Risks: Descriptor pointer/name static members must obey ODR rules on older compilers. Inherited/virtual base traversal must avoid duplicate virtual base visits and correctly flag hidden members.

Test signals: Static assertions for public/protected/private filters, inherited and virtual base members, hidden-name flags, function vs data descriptors, and described/undescribed classes.
