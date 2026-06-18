# sources/storage-engines/tikv/tests/integrations/config/test-log-compatible.toml

## sources/storage-engines/tikv/tests/integrations/config/test-log-compatible.toml

Purpose: legacy root-level log config compatibility fixture.

Important fields: root `log-level = "critical"`, `log-file = "foo"`, `log-format = "json"`, and `log-rotation-size = "1024MB"`, followed by otherwise empty standard sections.

Control flow and state: `test_log_backward_compatible` deserializes the fixture and first observes modern `[log]` defaults, then calls `logger_compatible_adjust()` and asserts the legacy root fields migrate into `cfg.log.level`, `cfg.log.file.filename`, `cfg.log.format`, and `cfg.log.file.max_size`.

Dependencies and integration points: logger compatibility layer and TOML serde aliases. Risks include removal of old root fields or wrong precedence when both old and new fields exist. Test signal is pre-adjustment defaults and post-adjustment legacy values.
