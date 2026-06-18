# sources/sync-backup/rsync/rsync.h

Purpose: Primary shared rsync header. It defines protocol constants, feature flags, cross-platform types, core structs, file-list layout macros, logging/debug categories, message codes, buffer helpers, and portability wrappers used across the C codebase.

Important APIs, types, and functions: Major definitions include protocol bounds/version, `XMIT_*`, `FLAG_*`, itemize flags, message/log enums, file type/delete enums, `struct file_struct`, `union file_extras`, `struct file_list`, `struct sum_struct`, `struct map_struct`, `filter_rule`, `struct stats`, `flist_ndx_list`, `item_list`, `xbuf`, `stat_x`, and `name_num_item`. Macros such as `F_LENGTH()`, `F_OWNER()`, `F_GROUP()`, `F_XATTR()`, `sum2_at()`, `INFO_GTE()`, and `DEBUG_GTE()` encode central access patterns.

Control flow: As a header it has no runtime flow, but it controls compilation via feature probes from `config.h`, fallback typedefs, optional iconv/ACL/xattr/support macros, and replacement libc declarations. It also includes `proto.h`, making project-wide function prototypes available to C files.

State and persistence behavior: Defines the in-memory shape of file-list entries and stats. File extras are stored before `struct file_struct`, so layout macros directly govern persistent transfer state in memory and wire-derived metadata interpretation.

Dependencies and integration points: Includes a broad set of platform headers plus rsync internal libraries (`byteorder.h`, digest, wildmatch, permstring, addrinfo, pool allocator). All major C files depend on it.

Risks and test signals: High-risk areas are protocol constant changes, file-extra alignment/layout, wire-value caps, platform fallback definitions, and macro side effects. Test signals include full build matrix, protocol compatibility tests, large-file and xattr/ACL tests, `rounding.c` compile check, and sanitizer/valgrind runs.
