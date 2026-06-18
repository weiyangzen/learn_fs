# sources/user-network-fs/rclone/backend/pikpak/helper.go

Purpose: helper layer for PikPak API calls, task waiting, user/VIP/quota/share/decompress operations, GCID/CID hashing, captcha signing/token persistence, and REST client captcha injection.

Important APIs/types/functions: request helpers include `requestDecompress`, `getUserInfo`, `getVIPInfo`, `requestBatchAction`, `requestNewTask`, `requestNewFile`, `getFile`, `patchFile`, `getTask`, `waitTask`, `deleteTask`, `getAbout`, and `requestShare`. Hash helpers are `getGcid`, `readGcid`, `calcGcid`, `unWrapObjectInfo`, and `calcCid`. Auth/client helpers include `genDeviceID`, `calcCaptchaSign`, `newCaptchaTokenRequest`, `CaptchaTokenSource`, `requestToken`, `refreshToken`, `Invalidate`, `Token`, `newPikpakClient`, `SetCaptchaTokener`, and wrapper `CallJSON`.

Control flow: request helpers build `rest.Opts`, call `f.rst` under the pacer, and delegate retry decisions to `f.shouldRetry`. Batch actions wait for an async task. `getFile` retries until a usable download link appears. `getGcid` calculates CID from source ranges, asks PikPak for a GCID, and upload code falls back to local `calcGcid`. `readGcid` hashes while replay-buffering in memory or an unlinked temp file. Captcha token flow loads token JSON from config, refreshes based on request action, writes refreshed JSON back to config, and injects `x-captcha-token`.

State and persistence: captcha token JSON is persisted under `captcha_token`. Large GCID calculations may create temporary files with `rclone-pikpak-gcid-` prefix and require cleanup. Remote state touched includes tasks, files, shares, decompression jobs, quota, and user profile.

Dependencies/integration: uses rclone `fs`, `configmap`, `fserrors`, `rest`, PikPak API types, crypto hashes, and HTTP/URL utilities. It depends on `Fs.rst`, `Fs.pacer`, `Options`, and `shouldRetry` from `pikpak.go`.

Risks/test signals: cleanup from `readGcid` must be called to avoid temp-file leaks. `waitTask` depends on retry policy for longer jobs. Captcha persistence may depend on mapper flush behavior. There are no direct tests for GCID/CID or captcha; integration tests cover them indirectly.
