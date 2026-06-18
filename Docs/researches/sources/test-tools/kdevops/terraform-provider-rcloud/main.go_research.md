# sources/test-tools/kdevops/terraform-provider-rcloud/main.go

## Purpose
This is the executable entrypoint for the rcloud Terraform provider plugin. It starts the Terraform Plugin Framework provider server with the registry address `registry.terraform.io/kdevops/rcloud`.

## Important APIs, Types, And Functions
The package-level `version` variable defaults to `dev` and is intended to be overridden by release tooling. `main()` declares a `-debug` flag, parses CLI flags, constructs `providerserver.ServeOpts` with provider address and debug mode, and calls `providerserver.Serve(context.Background(), provider.New(version), opts)`.

## Control Flow
Execution is linear: parse flags, build serve options, start the provider server, and fatal-log any startup/runtime error returned by the framework server. `go:generate` comments document optional Terraform formatting and plugin docs generation.

## State And Persistence
There is no persistent state in this file. Runtime state is the provider server process and its debug setting. Version metadata flows into provider metadata.

## Dependencies And Integration Points
It depends on Go `flag`, `log`, `context`, HashiCorp `providerserver`, and the internal provider package. Terraform discovers and runs this binary as a provider plugin; the address must match provider source names used by Terraform configurations.

## Risks And Test Signals
The server uses a background context, so shutdown relies on framework/server process handling rather than caller-provided cancellation. Debug mode is only opt-in through `-debug`. Tests are usually limited to build tests and provider smoke tests; release checks should verify the injected version, provider address, and generated docs examples.
