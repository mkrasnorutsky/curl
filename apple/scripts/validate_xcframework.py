#!/usr/bin/env python3
"""Link each iOS slice, exercise a native file transfer and optionally verify HTTPS."""
from pathlib import Path
import argparse,json,plistlib,subprocess,tempfile
from build_xcframework import ROOT,configure,SYSTEM_FRAMEWORKS
from dependencies import fetch,select
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--https',action='store_true');p.add_argument('--native-cares-source',type=Path);a=p.parse_args()
artifact=ROOT/'dist/Curl.xcframework';info=plistlib.loads((artifact/'Info.plist').read_bytes());assert len(info['AvailableLibraries'])==2
cares=fetch()['CAres']
def link(sdk,triple,headers,archive,cares_library,destination):
    subprocess.run(['xcrun','clang',*(['-target',triple] if triple else []),'-isysroot',sdk,'-DCURL_STATICLIB','-I'+str(headers),str(ROOT/'apple/scripts/curl_smoke.c'),str(archive),str(cares_library),'-lz','-lresolv',*[item for framework in SYSTEM_FRAMEWORKS for item in ['-framework',framework]],'-o',str(destination)],check=True)
for entry in info['AvailableLibraries']:
    sim=entry.get('SupportedPlatformVariant')=='simulator';assert entry['SupportedPlatform']=='ios'
    assert set(entry['SupportedArchitectures'])==({'arm64','x86_64'} if sim else {'arm64'})
    folder=artifact/entry['LibraryIdentifier'];archive=folder/entry['LibraryPath'];headers=folder/entry['HeadersPath'];cfolder,centry=select(cares,sim)
    subprocess.run(['lipo',str(archive),'-verify_arch',*entry['SupportedArchitectures']],check=True)
    sdk=subprocess.check_output(['xcrun','--sdk','iphonesimulator' if sim else 'iphoneos','--show-sdk-path'],text=True).strip()
    for arch in entry['SupportedArchitectures']:
        triple=arch+'-apple-ios18.0'+('-simulator' if sim else '')
        with tempfile.TemporaryDirectory(prefix='curl-client-') as directory:link(sdk,triple,headers,archive,cfolder/centry['LibraryPath'],Path(directory)/'client')
print('PASS: curl + c-ares + Apple TLS link for all three iOS targets',flush=True)
pin=json.loads((ROOT/'apple/dependencies.json').read_text())['CAres'];source=a.native_cares_source.resolve() if a.native_cares_source else ROOT/'out/native-cares-source'
if not source.exists():
    subprocess.run(['git','clone','--filter=blob:none','--no-checkout',pin['source_url'],str(source)],check=True)
    subprocess.run(['git','-C',str(source),'checkout',pin['source_revision']],check=True)
assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==pin['source_revision'],'Native c-ares source revision mismatch'
cb=ROOT/'out/native-cares';cp=cb/'install'
subprocess.run(['cmake','-S',str(source),'-B',str(cb),'-DCMAKE_BUILD_TYPE=Release','-DCARES_STATIC=ON','-DCARES_SHARED=OFF','-DCARES_BUILD_TESTS=OFF','-DCARES_BUILD_TOOLS=OFF','-DCARES_THREADS=ON','-DCMAKE_INSTALL_PREFIX='+str(cp)],check=True)
subprocess.run(['cmake','--build',str(cb),'--parallel','6'],check=True);subprocess.run(['cmake','--install',str(cb)],check=True)
build=ROOT/'out/native-validation';prefix=build/'install';configure(build,prefix,cp/'include',cp/'lib/libcares.a')
sdk=subprocess.check_output(['xcrun','--sdk','macosx','--show-sdk-path'],text=True).strip()
link(sdk,None,prefix/'include',prefix/'lib/libcurl.a',cp/'lib/libcares.a',build/'curl_smoke')
fixture=build/'fixture.txt';fixture.write_text('OneClickPilot curl file fixture\n')
subprocess.run([str(build/'curl_smoke'),fixture.as_uri()],check=True)
if a.https:subprocess.run([str(build/'curl_smoke'),'https://api.github.com/repos/mkrasnorutsky/curl'],check=True)
