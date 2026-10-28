# libcurl for iOS and Swift Package Manager

The full tracked curl source and upstream history are preserved at OneClickPilot's pinned revision `7eb8c048470ed2cc14dca75be9c1cdae7ac8498b` (8.10.1-DEV). This package provides SimGear's transfer library with Apple Secure Transport and a pinned c-ares resolver.

## Add the package

Add `https://github.com/mkrasnorutsky/curl.git` in Xcode, select version **0.1.0** or later, and add the **Curl** product. It integrates a checksum-verified static XCFramework for **arm64 iPhone, arm64 Simulator and x86_64 Simulator**, minimum iOS **18.0**. The binary module is **CCurl**; headers retain the standard `<curl/curl.h>` API and the wrapper header is `CurlSPM.h`.

[Release 0.1.0](https://github.com/mkrasnorutsky/curl/releases/tag/0.1.0) contains the XCFramework ZIP, checksum and build manifest. The package declares **CAres 0.1.0** as a transitive dependency, plus SDK zlib/resolv and Security/CoreFoundation/CoreServices frameworks. Do not also manually link older curl/c-ares copies. SPM integrates binaries and does not execute CMake during resolution.

This package selects c-ares asynchronous DNS rather than the older local build's threaded resolver. Secure Transport supplies TLS with the Apple trust system; its backend supports TLS through **1.2**, not TLS 1.3. HTTP/2, HTTP/3, SSH, LDAP, Brotli, zstd, libidn2 and libpsl integrations are disabled. SDK zlib compression is enabled. The exact options are recorded in `dist/build-manifest.json`. Standard curl certificate/hostname verification defaults are retained.

## Build

Requirements: macOS, Xcode with both iOS SDKs, CMake, Python 3 and Git. No signing identity is required for static artifacts.

```sh
git clone https://github.com/mkrasnorutsky/curl.git
cd curl
python3 apple/scripts/build_xcframework.py --jobs 6
python3 apple/scripts/validate_xcframework.py
```

The build downloads the c-ares release archive from `apple/dependencies.json` and verifies its SHA-256. It uses no machine-specific dependency installation. CMake builds each iOS architecture, lipo combines only Simulator archives, and Xcode produces `dist/Curl.xcframework` with public headers, a module map and licensing notices.

Validation links curl and c-ares with their Apple dependencies for every target. It then builds native macOS c-ares from its pinned source revision and builds native curl. The native client verifies URL parsing, percent escaping, the selected TLS/resolver backends, header/library version and a local file transfer. By default, no live HTTPS service is needed; native validation does fetch pinned c-ares source if not already present. `--native-cares-source PATH` reuses a checkout at the required revision.

To also test a real HTTPS GET against this public GitHub repository:

```sh
python3 apple/scripts/validate_xcframework.py --https
```

The HTTPS test explicitly enables peer-certificate and hostname verification. Native execution tests the host build, not runtime behavior of an iOS slice. A manually dispatched GitHub Actions workflow runs the offline checks. Upstream automation definitions are preserved under `apple/upstream-workflows` so this distribution repository does not launch unrelated upstream build matrices on every push.

To use local rebuilt binaries in Xcode, copy `apple/Package.local.swift` to the root `Package.swift` before adding the folder as a local package.

## Releases

```sh
python3 apple/scripts/package_release.py --tag 0.2.0
```

Upload the ZIP and checksums to the matching GitHub release, then commit `dist/Package.swift` as the root manifest at that revision. Published archive bytes/checksums remain immutable. Original COPYING and LICENSES notices are retained in both source and distribution.
