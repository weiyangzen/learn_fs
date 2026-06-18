# File Research: sources/windows/reactos/drivers/filesystems/udfs/wcache.h

This header wraps the shared write-cache library header for the UDF driver.

Key contents:
- Include guard `__CDRW_WCACHE_H__`.
- Includes `Include/wcache_lib.h`.

Notable design points:
- This file provides the UDF-local include name for the reusable write-cache library.
- No types or functions are declared directly here; all public cache API comes from `wcache_lib.h`.
