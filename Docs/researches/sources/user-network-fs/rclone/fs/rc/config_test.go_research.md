# Research: sources/user-network-fs/rclone/fs/rc/config_test.go

## sources/user-network-fs/rclone/fs/rc/config_test.go

Purpose: tests rc option registry endpoints and mutation behavior. It uses `clearOptionBlock` to replace `fs.OptionsRegistry` with a temporary map, registers a synthetic `potato` option block, and optionally attaches a reload callback.

Control flow verifies registration, `options/blocks`, filtered and unfiltered `options/get`, JSON marshalability with real main/rc options, `options/info`, and `options/set`. Mutation tests assert a single field update reshapes defaults, reload is called, reload errors propagate, unknown blocks error, and bad payload shapes error. State is global option registry and shared `testOptions`, restored after each test. Dependencies are `fs.RegisterGlobalOptions`, `rc.Calls`, JSON, and testify. Integration signal is strong for API clients changing runtime options. Risks covered include global state restoration, reload side effects, and block filtering. A residual risk is that tests depend on reshape behavior setting omitted fields to defaults, which is important for callers but can surprise partial update users.
