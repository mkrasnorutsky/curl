// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "Curl", platforms: [.iOS("18.0")],
    products: [.library(name: "Curl", targets: ["Curl"])],
    dependencies: [.package(url: "https://github.com/mkrasnorutsky/c-ares.git", exact: "0.1.0")],
    targets: [
        .binaryTarget(name: "CCurl", url: "https://github.com/mkrasnorutsky/curl/releases/download/0.1.0/Curl.xcframework.zip", checksum: "29e8d7316463d81708d1ec54c91c41b3c47592ff15b757f914146fc178532149"),
        .target(name: "Curl", dependencies: ["CCurl", .product(name: "CAres", package: "c-ares")], path: "apple/SPM", publicHeadersPath: "include",
                cSettings: [.define("CURL_STATICLIB")], linkerSettings: [.linkedLibrary("z"), .linkedLibrary("resolv"), .linkedFramework("Security"), .linkedFramework("CoreFoundation"), .linkedFramework("CoreServices")])
    ])
