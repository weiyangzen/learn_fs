## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/common/__init__.py

Purpose: Marks `common` as a Python package for GKE continuous-test helpers.

APIs and integration: It exports no symbols and has no import side effects. Consumers import `from common import utils` after adding the GKE parent directory to `sys.path`.

Control flow and state: None beyond package discovery.

Dependencies and risks: Low risk. The package remains importable as long as callers set `sys.path` correctly.

Test signals: Import success from neighboring benchmark scripts.
