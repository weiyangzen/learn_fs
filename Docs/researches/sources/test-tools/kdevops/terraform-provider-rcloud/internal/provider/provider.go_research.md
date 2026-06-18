# sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/provider.go

## Purpose
This file defines the Terraform Plugin Framework provider for rcloud. It exposes provider-level endpoint, token, and SSH defaults, constructs an `APIClient`, and registers the VM resource.

## Important APIs, Types, And Functions
`RcloudProvider` implements `provider.Provider` and stores the build/version string. `RcloudProviderModel` maps Terraform provider configuration attributes `endpoint`, `token`, `ssh_user`, and `ssh_public_key_file`. `Metadata()` sets provider type name `rcloud` and version. `Schema()` declares optional/sensitive configuration attributes. `Configure()` reads config, falls back to `RCLOUD_ENDPOINT` and `RCLOUD_TOKEN`, defaults the endpoint to `http://localhost:8765`, builds `APIClient`, and publishes it through `resp.DataSourceData` and `resp.ResourceData`. `Resources()` returns `NewVMResource`; `DataSources()` currently returns an empty list; `New(version)` is the provider factory used by `main.go`.

## Control Flow
Terraform calls schema and configure during provider setup. Configure decodes config into framework `types.String` fields, short-circuits on diagnostics, resolves environment/config/default precedence, then passes the client to resources and future data sources. Resource discovery is static and currently includes only `rcloud_vm`.

## State And Persistence
The provider persists no data itself. Sensitive token values are held in the in-memory client and provider config state through Terraform. SSH defaults are provider-level state that resources inherit during create.

## Dependencies And Integration Points
It depends on Terraform Plugin Framework provider, resource, datasource, schema, and types packages. It integrates with environment variables `RCLOUD_ENDPOINT` and `RCLOUD_TOKEN`, with `resource_vm.go` through `ResourceData`, and with the provider server in `main.go`.

## Risks And Test Signals
Optional string attributes are checked only for null, not unknown values, which can matter during planning in Terraform Framework providers. There is no validation for endpoint URL format or SSH key path. `DataSourceData` is populated despite no data sources. Acceptance tests should verify configuration precedence, sensitive token schema marking, default endpoint behavior, provider metadata, and resource registration. Framework unit tests can use provider schema/configure harnesses without contacting rcloud.
