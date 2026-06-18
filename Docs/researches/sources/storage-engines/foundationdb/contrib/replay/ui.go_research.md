# sources/storage-engines/foundationdb/contrib/replay/ui.go

## Purpose
`ui.go` implements the interactive Bubble Tea terminal UI for FoundationDB trace replay. It turns parsed `TraceData` into a time-oriented cluster replay view with topology on the left, current and surrounding events on the right, compact configuration/recovery/epoch status at the bottom, and modal popups for filtering, searching, health metrics, help, full DB config JSON, and direct time jumps. It is presentation-heavy but also owns most in-memory UI state transitions for navigation, filtering, searching, and health summaries.

## Important APIs, Types, And Functions
- `model` is the central Bubble Tea model. It stores immutable-ish input data (`traceData`), replay cursor state (`currentTime`, `currentEventIndex`, `clusterState`), terminal dimensions, popup modes, text inputs, search state, filter state, and caches such as `machineDCCache`.
- `newModel(traceData *TraceData) model` initializes all text inputs, extracts and sorts unique event `Type` values for type search, sets default filter time bounds to `traceData.MinTime` and `traceData.MaxTime`, and creates `NewClusterState()`.
- `Init`, `Update`, `View`, and `runUI` are the Bubble Tea integration points. `runUI` starts `tea.NewProgram(newModel(traceData), tea.WithAltScreen())`.
- Navigation and modal handlers include `handleMachineSelectionPopup`, `handleFilterTimeInput`, and `handleTypeSearchPopup`, plus large `Update` branches for top-level mode, search mode, time input mode, config view, health view, help view, and filter view.
- Rendering helpers include `formatRoleLabel`, `formatNumberWithCommas`, `formatTraceEvent`, `buildEventListPane`, `wrapText`, `renderFilterPopup`, `renderFilterTimeRangePopup`, `renderMachineSelectionPopup`, `renderTypeSearchPopup`, `renderHealthPopup`, `renderHelpPopup`, `renderNoConfigPopup`, `renderConfigPopup`, and `renderTimeInputPopup`.
- Health summarization types are `NetworkMetric`, `DegradedPeerMetric`, and `ConnectionMetric`; collectors are `collectNetworkMetrics`, `collectDegradedPeerMetrics`, and `collectConnectionMetrics`.
- Search/filter helpers include `convertWildcardToRegex`, `extractLiterals`, `getEventFullText`, `searchForward`, `searchBackward`, `recompileRawFilterRegexes`, `rebuildMachineSet`, `getCachedDC`, `eventMatchesFilters`, `normalizeAddress`, and `stripRPCName`.
- `SelectableItem` models rows in the machine-selection popup, with `Type` values `"dc"` or `"machine"` and optional `Worker` role detail.

## Control Flow
`Update` prioritizes nested modes before normal navigation. If filter mode is active, it delegates first to machine selection, time input, or type search sub-popups, then handles filter-menu keybindings. Help, health, config, top-level time input, and search modes short-circuit normal navigation. Normal mode handles quit, popups, forward/back event navigation, one-second page jumps, start/end jumps, recovery jumps, severity jumps, search entry, search continuation, and clearing search highlights.

Most cursor movement updates `currentEventIndex`, mirrors `currentTime` from the target event, and calls `updateClusterState()`. `updateClusterState` rebuilds topology from `traceData.Events[:currentEventIndex+1]` using `BuildClusterState`, so UI state represents trace history up to the selected event. `ensureCurrentEventVisible` repairs the cursor after filter changes by searching forward first, then backward, for a visible event.

`View` constructs a full frame from current model state. It derives the current event, current machine and role ID, groups cluster workers by DC/tester through `ClusterState`, highlights network-message source and destination after `normalizeAddress`, packs topology rows into columns based on terminal height, builds a wrapped event list around the current event, renders DB config/recovery/epoch/status sections, and overlays the active popup using `lipgloss.Place`.

Filters use AND logic across categories and OR logic inside raw and machine categories. `eventMatchesFilters` returns all events when `filterShowAll` is true; when it is false and no category is configured, it returns no events. Time bounds are applied first, then selected machine/DC membership, then raw wildcard regexes excluding disabled filters, then the NetworkMessageSent-only message filter.

Search compiles the wildcard-translated pattern as a regular expression, scans visible events only, and wraps around the trace. Search highlighting is separate from matching: `formatTraceEvent` highlights literal non-wildcard segments extracted from the search pattern.

## State And Persistence Behavior
All UI state is in memory inside `model`; the file does not write persistent state. Persistent inputs come from parsed trace files via `TraceData`, including `Events`, configs, recovery states, epoch versions, and min/max time. Rendered config JSON comes from `DBConfig.RawJSON`. Filter raw regexes and machine/DC extraction caches are derived state and can be rebuilt. `clusterState` is recomputed repeatedly from trace event prefixes rather than incrementally mutating durable state.

The only process-level side effect is starting the alternate-screen Bubble Tea program. No config, search, filter, or cursor choices are saved across runs.

## Dependencies And Integration Points
The file depends on `github.com/charmbracelet/bubbletea`, `bubbles/textinput`, and `lipgloss` for terminal interaction and styling. It integrates with local replay code through `TraceData`, `TraceEvent`, `DBConfig`, `RecoveryState`, `EpochVersionInfo`, `ClusterState`, `Worker`, `RoleInfo`, `NewClusterState`, `BuildClusterState`, `GetWorkersByDC`, `GetTesters`, and trace lookup methods such as `GetEventIndexAtTime`, `GetLatestConfigAtTime`, `GetLatestRecoveryStateAtIndex`, `GetLatestEpochVersionAtIndex`, `FindNextRecovery`, and `FindPreviousRecoveryWithStatusCode`.

Trace semantics are FoundationDB-specific: role events drive topology; `MasterRecoveryState` drives recovery/config display and recovery navigation; `UpdateRegistration`/durability-derived epoch data is exposed by `TraceData`; network health popups inspect `PingLatency`, `HealthMonitorDetectDegradedPeer`, `Sim2Connection`, and `SimulatedDisconnection`; `NetworkMessageSent` gets special source/destination/RPC highlighting.

## Risks And Edge Cases
- Performance is the main risk. `BuildClusterState(m.traceData.Events)` is called in machine selection and filter rendering over the full trace, and `updateClusterState` rebuilds from the beginning up to the cursor on many movements. Health collectors also scan from the start to `currentEventIndex`. Large traces can make navigation and popups expensive.
- `View` and popup rendering mutate fields on value receiver copies in a few places for clamping (`m.filterMachineColumn`, `m.filterTypeSearchSelected`, scroll offsets). That is harmless for rendering but can make visible clamping differ from persisted model state until the next key event.
- `formatTraceEvent` ignores errors from compiling search regexes; invalid regex from wildcard conversion is unlikely because most metacharacters are escaped, but empty/odd patterns can silently skip highlighting.
- Raw filter regexes are only effective after `recompileRawFilterRegexes`; direct mutation of `filterRawList` without recompilation would make filtering stale. Current add/edit/remove/common/type-search paths do recompile.
- `extractDCFromAddress` uses simple colon splitting and may misclassify unusual IPv6 addresses or addresses with bracket/port variations; `cluster.go` has a separate `parseAddress` implementation, so DC extraction rules can diverge.
- Time range input accepts start/end without validating against min/max or start <= end. A reversed range simply hides events.
- The type-search path adds `Type=<value> ` with a trailing space. Because `getEventFullText` joins fields with spaces, this intentionally approximates exact type matching, but it is sensitive to representation details.
- Topology packing checks group starts against rendered strings that may include ANSI escape sequences; `strings.HasPrefix` can fail after styling, while `strings.Contains` checks for bullets/arrows may still catch many cases.
- `stripRPCName` unwraps only `ErrorOr` and `EnsureTable`, and repeated wrapper removal resets `result` to inner content. Other wrapper forms remain visible.
- `truncateAddr` assumes `maxLen >= 3`; current call sites pass 21.

## Test Signals
Useful tests would drive `Update` with `tea.KeyMsg` sequences and inspect model state for navigation, filter toggles, search wraparound, popup mode transitions, and cursor repair. Unit-level tests can cover `convertWildcardToRegex`, `extractLiterals`, `getEventFullText`, `eventMatchesFilters`, `normalizeAddress`, `stripRPCName`, `formatNumberWithCommas`, and metric collectors using synthetic `TraceData`. Integration smoke tests should run `runUI` or `View` against a small parsed trace and verify that config/recovery/epoch lines, NetworkMessageSent highlighting, and health popup rows render without panics at small terminal sizes. Performance tests with large event slices would catch repeated full-prefix rebuild regressions.
