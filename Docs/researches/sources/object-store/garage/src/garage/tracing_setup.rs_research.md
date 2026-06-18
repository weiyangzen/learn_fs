# sources/object-store/garage/src/garage/tracing_setup.rs

Purpose: This file abstracts optional OpenTelemetry tracing initialization behind a single exported `init_tracing` function.

Important APIs and types: It re-exports `telemetry::init_tracing`. The non-`telemetry-otlp` implementation logs an error and returns `Ok(())`. The feature-enabled implementation builds an OTLP tracing pipeline with tonic exporter, timeout, trace config, sampler, ID generator, and resource labels.

Control flow: When `telemetry-otlp` is disabled, calling `init_tracing` emits that the admin trace sink is ignored. When enabled, it shortens the node UUID to an instance ID, builds an always-on tracing pipeline to the configured endpoint, installs it with Tokio batch runtime, and returns an error if initialization fails.

State and persistence behavior: There is no persistence. Runtime state is the global OpenTelemetry tracer provider installed by the pipeline; `server.rs` later calls global shutdown during daemon shutdown.

Dependencies and integration points: It integrates `garage_util::data::Uuid`, `garage_util::error`, `opentelemetry`, `opentelemetry_otlp`, and server config `admin.trace_sink`.

Risks: Without the feature, configuring a trace sink only logs an error but does not fail startup. With the feature, sampler is always-on, so trace volume can be high. Initialization timeout is fixed at three seconds.

Test signals: No direct tests in this group. Server startup with trace sink would exercise it; default integration config does not set a trace sink.
