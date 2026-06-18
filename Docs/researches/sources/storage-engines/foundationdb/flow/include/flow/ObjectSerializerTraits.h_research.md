<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ObjectSerializerTraits.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ObjectSerializerTraits.h

Purpose: This header declares the trait vocabulary used by Flow's object serializer. It defines how scalar, dynamic-size, serializable, vector-like, union-like, and struct-like types opt into generic save/load behavior, plus visitor detection for flat-buffer visitors.

Important APIs and types: Core templates are `is_fb_function`, `pack`, `index_t`, `fb_must_appear_last`, `serializer`, `scalar_traits`, `dynamic_size_traits`, `serializable_traits`, `serialize_raw`, `vector_like_traits`, `union_like_traits`, and `struct_like_traits`. The file provides a concrete `union_like_traits<std::variant<...>>` specialization.

Control flow: `serializer(visitor, items...)` is enabled only for Flow flat-buffer visitor objects and statically checks that any type marked `fb_must_appear_last` appears only in final position. Trait defaults inherit `std::false_type` and provide declarations only; real implementations specialize them elsewhere. The variant union trait reports the active index, retrieves by index, and assigns alternatives during load.

State and persistence behavior: The header does not persist data directly; it defines compile-time contracts that determine byte layout and load behavior used by `ObjectSerializer.h` and `flat_buffers.h`. Incorrect trait specializations can change durable wire or disk encodings.

Dependencies and integration points: It depends on standard type traits, memory, functional, vector, and variant. It is included by serializer-facing headers and by types that implement `serialize(Ar&)` with either visitor-style or stream-style serializers.

Risks: The traits are highly generic and fail mostly at compile time, but subtle trait errors can silently alter field order or union indexes. The `std::variant` trait uses `variant.index()` as an 8-bit index, so very large variants would exceed the format. `fb_must_appear_last` is enforced only for visitor serializer calls.

Test signals: Compile-only tests for trait specialization coverage are important. Runtime signals include variant round trips across all alternatives, struct/vector custom trait round trips, static assertion coverage for must-appear-last fields, and compatibility checks that trait changes do not alter expected serialized bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ObjectSerializerTraits.h -->
