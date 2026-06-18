<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/regex.c -->
# sources/security-integrity/selinux/libselinux/src/regex.c

## Purpose
Abstracts the file-context regular expression backend so label code can support PCRE2 or legacy PCRE through one internal API.

## Important APIs, Types, And Functions
`regex_arch_string()` identifies pointer width, regex size type width, and endian for serialized PCRE2 patterns. `regex_version()` reports backend version. `regex_prepare_data()` compiles and prepares match data/study data. `regex_load_mmap()` loads serialized patterns from compiled file-context mmaps. `regex_writef()` serializes patterns. `regex_match()`, `regex_cmp()`, `regex_data_free()`, and `regex_format_error()` provide matching, crude comparison, cleanup, and diagnostics.

## Control Flow
The PCRE2 path compiles with `PCRE2_DOTALL`, optionally decodes serialized code, writes serialized blobs with a length prefix, and locks a mutex around match data. The PCRE1 path maps compiled and study blobs directly from mmap and uses ownership flags to avoid freeing mapped memory.

## State And Persistence Behavior
Regex state is heap or mmap-backed `struct regex_data`. Serialization writes backend-specific binary blobs to compiled context files, and PCRE2 serialization is guarded by architecture string compatibility.

## Dependencies And Integration Points
Used by file-label parsing/loading and `sefcontext_compile`; depends on `label_file.h`, `next_entry()`, pthread mutex helpers, endian conversion, PCRE/PCRE2 APIs, and `SELABEL_*` comparison constants.

## Risks And Test Signals
Risks include backend divergence, non-portable serialized patterns, mutex lifecycle, binary comparison false negatives, and malformed mmap bounds. Tests should cover compile errors, partial matches, no matches, serialization round trips, mismatched architecture/version data, and both PCRE1/PCRE2 builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/regex.c -->
