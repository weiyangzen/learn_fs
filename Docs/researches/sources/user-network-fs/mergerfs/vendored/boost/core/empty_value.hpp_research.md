# sources/user-network-fs/mergerfs/vendored/boost/core/empty_value.hpp

Purpose: Provides `boost::empty_::empty_value<T,N>` storage wrapper that applies empty-base optimization when safe.

Important APIs, types, and functions: `use_empty_value_base<T>`, `empty_init_t`, `empty_value<T,N,UseBase>`, `empty_value_base<T>`, `boost::empty_::empty_value`, and inline constant `boost::empty_init`.

Control flow: Compile-time trait chooses composition or private inheritance. Constructors support default/empty-init and forwarding where available. Accessors return references to the stored value/base.

State and persistence behavior: Stores one `T` value unless represented by empty base subobject. No external persistence.

Dependencies and integration points: Depends on Boost config, type traits, and utility forwarding. Used by containers and utilities to store allocators, predicates, or functors compactly.

Risks: Empty-base optimization must avoid final/non-empty/unsafe types and preserve object identity for repeated bases via `N`. Constructor forwarding differs by language mode.

Test signals: Size tests for empty vs non-empty types, multiple `N` indices, final classes, const accessors, forwarding constructors, and standard-layout expectations where relevant.
