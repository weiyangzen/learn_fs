# sources/test-tools/kdevops/terraform-provider-rcloud/internal/provider/resource_vm.go

## Purpose
This file implements the `rcloud_vm` Terraform resource. It maps Terraform desired VM properties into rcloud create requests, waits for a usable IP address, updates Terraform state, deletes VMs, and supports import by ID.

## Important APIs, Types, And Functions
`VMResource` implements `resource.Resource` and `resource.ResourceWithImportState` and stores the configured `*APIClient`. `VMResourceModel` maps state attributes: `id`, `name`, `vcpus`, `memory_gb`, `base_image`, `root_disk_gb`, `ssh_user`, `ssh_public_key_file`, `state`, and `ip_address`. `Schema()` marks most creation inputs as `Required` or `Optional` with `RequiresReplace()` plan modifiers, while computed fields use `UseStateForUnknown()` for ID and computed-only schema for state/IP. `Configure()` type-checks provider data. `Create()` resolves SSH settings, reads public key file contents, calls `CreateVM()`, polls `GetVM()` for an IP address, cleans up on timeout, and sets state. `Read()`, `Update()`, `Delete()`, and `ImportState()` implement the rest of the resource lifecycle.

## Control Flow
Create reads planned values, picks resource SSH settings over provider defaults, reads the SSH public key file if configured, sends a create request with memory converted from GB to MB, and stores the returned ID. It then polls once per second for up to 300 seconds until `vm.IPAddress` is non-empty. If no IP arrives, it reports a diagnostic and attempts to delete the VM. Read fetches the remote VM and refreshes state/IP. Update is effectively a no-op because replace-required plan modifiers should handle mutable inputs. Delete calls remote delete and leaves state removal to Terraform.

## State And Persistence
Terraform state stores the VM ID, desired immutable inputs, remote state, and IP address. The remote rcloud API owns actual VM lifecycle state. Create reads the SSH public key file from disk and sends its contents to the API but does not persist it locally. Failed IP acquisition can leave a remote VM if cleanup delete fails.

## Dependencies And Integration Points
It depends on Terraform Plugin Framework resource/schema/planmodifier packages, `terraform-plugin-log/tflog`, Go `os` for key reads, and the local `APIClient`. It integrates with kdevops bringup assumptions by refusing successful create without an IP address, because later SSH configuration needs that IP.

## Risks And Test Signals
The 5-minute polling loop uses `time.Sleep()` directly and does not honor context cancellation, which can make Terraform interrupts slow. A 404 on read is reported as an error rather than removing state, so out-of-band deletion is not gracefully reconciled. Update can write planned data without reading remote truth if any future mutable field is added. SSH key file contents are logged only by length, but diagnostics include the key path. Tests should cover resource/provider config type errors, create payload conversion, provider-vs-resource SSH precedence, key read failures, IP timeout cleanup, read IP nulling, delete errors, import state, and context cancellation expectations.
