#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
import os
WORK=Path(os.environ.get("APPLE_BUILD_ROOT", str(ROOT))).expanduser().resolve()
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
out=WORK/'dist';archive=out/'Curl.xcframework.zip'
if archive.exists():archive.unlink()
subprocess.run(['ditto','-c','-k','--sequesterRsrc','--keepParent',str(out/'Curl.xcframework'),str(archive)],check=True)
checksum=hashlib.sha256(archive.read_bytes()).hexdigest()
manifest=(ROOT/'apple/Package.local.swift').read_text().replace('path: "dist/Curl.xcframework"',f'url: "https://github.com/mkrasnorutsky/curl/releases/download/{a.tag}/Curl.xcframework.zip", checksum: "{checksum}"')
(out/'Package.swift').write_text(manifest)
(out/'checksums.json').write_text(json.dumps({'Curl':checksum},indent=2)+'\n')
print('Release archive, checksum and manifest prepared in',out)
