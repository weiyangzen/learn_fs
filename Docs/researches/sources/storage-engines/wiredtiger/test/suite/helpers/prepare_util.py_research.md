# sources/storage-engines/wiredtiger/test/suite/helpers/prepare_util.py

Purpose: minimal base class for tests that need preserve-prepared and precise-checkpoint connection settings.

Important APIs and control flow: declares `test_prepare_preserve_prepare_base`, a `wttest.WiredTigerTestCase` subclass with class attribute `conn_config = 'precise_checkpoint=true,preserve_prepared=true,statistics=(all)'`.

State and persistence behavior: no methods or runtime state are added. The class-level config changes connection behavior for subclasses.

Dependencies and integration points: imported by prepare/checkpoint tests that subclass it to share a common connection configuration.

Risks: despite the class name starting with `test_`, it is a base class and could be collected accidentally by generic test discovery if not handled by the suite conventions. Config is fixed and may need extension by subclasses through inheritance patterns.

Test signals: subclasses should open connections with precise checkpointing, prepared update preservation, and statistics enabled.
