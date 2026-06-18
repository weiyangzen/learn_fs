<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/format.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/format.cpp

Purpose: This vendored fmt translation unit provides explicit template instantiations for fmt formatting internals, reducing header-only duplication for the libfuse build.

Important APIs: it includes `fmt/format-inl.h`, opens the fmt namespace, and explicitly instantiates locale references, Dragonbox float/double conversion, thousands separator and decimal point helpers for `char` and `wchar_t`, and deprecated `buffer<Char>::append` overloads.

State and integration: there is no runtime state beyond fmt internals. The object file is included in `libfuse.a` through the Makefile's `lib/*.cpp` glob and satisfies symbols used by both narrow and wide formatting paths.

Risks and test signals: the file must match the vendored fmt version and compile flags; mismatched headers can produce duplicate or missing symbols. Tests should link a binary using fmt narrow/wide formatting, locale formatting when enabled, and floating-point formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/format.cpp -->
