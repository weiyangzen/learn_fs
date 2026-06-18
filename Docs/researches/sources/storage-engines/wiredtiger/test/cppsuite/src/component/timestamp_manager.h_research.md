# sources/storage-engines/wiredtiger/test/cppsuite/src/component/timestamp_manager.h

Purpose: Declares the timestamp-manager component and timestamp utility APIs.

Important APIs/types/functions: exposes conversion helpers, lifecycle overrides, `get_next_ts`, `get_oldest_ts`, and `get_valid_read_ts`. Private `get_time_now_s` returns seconds shifted into timestamp high bits.

Control flow: used both as a periodic component and as a service object for other components.

State and persistence: atomic increment and oldest timestamp plus stable timestamp and lag windows.

Dependencies/integration: inherits `component` and uses WT timestamp/test utility types.

Risks and test signals: `_stable_ts` is not atomic while readers may call `get_valid_read_ts`; current code assumes acceptable benign races. Lag configs must be nonnegative.
