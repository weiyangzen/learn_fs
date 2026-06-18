# sources/user-network-fs/nfs-utils/support/include/xcommon.h

## Purpose
Declares common mount/support helpers, checked allocation wrappers, string concatenation helpers, error reporting, and exit status flags.

## Important APIs, Types, and Functions
`canonicalize()`, `nfs_error()`, `xmalloc()`, `xrealloc()`, `xfree()`, `xstrdup()`, `xstrndup()`, `xstrconcat*()`, `die()`, `at_die`, `streq`, format attributes, and `EX_*` status bits.

## Control Flow
Callers use checked allocation and fatal error helpers throughout nfs-utils support and mount code. Exit status bits are ORed to report mount outcomes.

## State and Persistence Behavior
No direct state except `at_die` callback. Allocation helpers may exit rather than return NULL, shaping caller control flow.

## Dependencies and Integration Points
Included by `xmalloc.h` and many support files. Depends on config feature macros and system major/minor headers.

## Risks and Edge Cases
Duplicate `die` declarations are intentional but noisy. Functions that exit on allocation failure must not be used where recovery is required.

## Test Signals
Build with format attributes enabled/disabled, test allocation wrappers, string concat helpers, and exit-status combinations.
