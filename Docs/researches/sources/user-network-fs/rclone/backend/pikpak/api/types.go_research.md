# sources/user-network-fs/rclone/backend/pikpak/api/types.go

Purpose: defines PikPak backend API schemas for files, folders, tasks, quota, sharing, upload tickets, resumable credentials, captcha, OAuth token conversion, filters, and decompression/archive support.

Important APIs/types/functions: `Time` handles RFC3339 timestamps and ignores JSON `null`/empty strings. Constants define Drive kinds, phases, upload types, thumbnail sizes, and list limit. `Error`/`ErrorDetails` model API errors. `Filters.Set` populates list filters through reflection. `Link.Valid` validates cached download links using the URL `expire` query first, then the `Expire` field. Major models include `File`, `FileList`, `Task`, `Form`, `Resumable`, `ResumableParams`, `NewFile`, `NewTask`, `About`, `Share`, `User`, `VIP`, request types, `CaptchaToken`, `CaptchaTokenRequest`, and `Token`.

Control flow: active logic is limited to time parsing/formatting, filter construction, link expiry checks, captcha-token expiry checks, and token expiry calculation from `expires_in`. Backend code uses these results to decide listing filters, link refresh, upload method, and auth persistence.

State and persistence: no direct persistence here. Structs represent remote Drive state and credentials. `CaptchaToken.Expiry` is populated by helper code before the token JSON is stored in rclone config.

Dependencies/integration: uses `fmt`, `net/url`, `reflect`, `strconv`, and `time`. Consumed by `pikpak.go`, `helper.go`, and `multipart.go`.

Risks/test signals: `Filters.Set` can panic if called with invalid field names or mismatched map types. Many API fields are `any` or partially known, so schema drift can be missed. URL expiry is treated as authoritative when parseable. `types_test.go` directly covers `Link.Valid`.
