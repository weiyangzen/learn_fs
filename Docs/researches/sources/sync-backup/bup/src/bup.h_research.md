## sources/sync-backup/bup/src/bup.h

Purpose: shared C header defining Bup process exit status constants.

Important APIs: `BupExit` maps success/true to 0, false to 1, and failure to 2. C launcher and support code use these constants for consistent command exit behavior.

State, dependencies, and risks: no state or dependencies. Consumers must preserve the semantic distinction between predicate false (`1`) and operational failure (`2`). Test scripts use expected failure codes across init/help/fsck/get scenarios.
