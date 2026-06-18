## sources/storage-engines/pebble/sstable/blockiter/doc.go

Purpose: Package documentation for `blockiter`, declaring it as the home for block-related interfaces common to row and columnar block engines.

Important APIs/types/functions: No code besides the package comment and `package blockiter`.

Control flow: None.

State and persistence behavior: None directly. It frames the package boundary for iterator abstractions used by SSTable readers.

Dependencies and integration points: Package-level integration point for rowblk and colblk iterator implementations.

Risks: Minimal; stale package documentation would be the main concern if the package grows beyond common interfaces.

Test signals: No direct tests needed for this documentation file.
