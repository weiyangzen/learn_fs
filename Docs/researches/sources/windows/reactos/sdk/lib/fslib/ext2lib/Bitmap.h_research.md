# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Bitmap.h

Read completely: 7 lines.

This header is a small precompiled-header-style include wrapper. It has `#pragma once` and includes `time.h`, `stdio.h`, `stdlib.h`, `string.h`, and `windows.h`.

Despite its name, it declares no bitmap APIs; the ext2 bitmap function declarations appear to live elsewhere, likely in `Mke2fs.h`.

Security/reliability notes: no runtime behavior. The name is potentially misleading for maintainers.
