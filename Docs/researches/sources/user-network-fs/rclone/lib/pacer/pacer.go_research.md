# sources/user-network-fs/rclone/lib/pacer/pacer.go

Source read signal: reviewed complete local file (302 lines, sha256 01ae0fa8fabf2e68).

Purpose: Provides a generic pacing, retry, and optional concurrency-limiting wrapper for API calls.

Important APIs/types/functions: Public types/functions include `State`, `Calculator`, `Pacer`, `InvokerFunc`, `Option`, `CalculatorOption`, `RetriesOption`, `MaxConnectionsOption`, `InvokerOption`, `Paced`, `New`, setters, `ModifyCalculator`, `Call`, `CallNoRetry`, `RetryAfterError`, and `IsRetryAfter`.

Control flow: `New` configures defaults, initializes a one-token pacing channel, optional connection tokens, calculator, and invoker. `beginCall` waits for the pace token based on current sleep and schedules token replacement after the delay, then optionally takes a connection token. `endCall` returns connection token, updates retry count/error, and asks the calculator for the next sleep. `call` invokes the paced function up to the retry limit and avoids recursive connection-token deadlock by checking the call stack. Retry-after errors wrap underlying errors and can be found through `lib/errors.Walk`.

State and persistence behavior: In-memory channels, mutex-protected options/state, and sleep goroutines only. No durable state.

Dependencies and integration points: Uses local `caller` and `errors` packages. Calculator implementations in sibling pacer files provide default, Google Drive, S3, and Azure IMDS behavior; multipart uploads use `TokenDispenser` from another sibling file.

Risks and test signals: Timer goroutines can accumulate under heavy pacing. Recursive-call detection by stack name is fragile but tested. Changing max connections after active calls is documented unsafe. Retry wrapping must preserve `errors.Is` through `Unwrap`.
