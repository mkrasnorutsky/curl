#!/usr/bin/env python3
"""Build static libcurl with Apple Secure Transport and pinned c-ares for iOS."""
from pathlib import Path
import argparse,json,shutil,subprocess
from dependencies import ROOT,fetch,select
import os
WORK=Path(os.environ.get("APPLE_BUILD_ROOT", str(ROOT))).expanduser().resolve()
OPTIONS=['-DBUILD_SHARED_LIBS=OFF','-DBUILD_STATIC_LIBS=ON','-DBUILD_CURL_EXE=OFF','-DBUILD_EXAMPLES=OFF','-DBUILD_TESTING=OFF','-DBUILD_LIBCURL_DOCS=OFF','-DBUILD_MISC_DOCS=OFF','-DCURL_USE_SECTRANSP=ON','-DCURL_DEFAULT_SSL_BACKEND=secure-transport','-DCURL_USE_OPENSSL=OFF','-DCURL_USE_PKGCONFIG=OFF','-DENABLE_ARES=ON','-DCURL_DISABLE_LDAP=ON','-DCURL_DISABLE_LDAPS=ON','-DCURL_ZLIB=ON','-DCURL_BROTLI=OFF','-DCURL_ZSTD=OFF','-DUSE_NGHTTP2=OFF','-DUSE_LIBIDN2=OFF','-DCURL_USE_LIBPSL=OFF','-DCURL_USE_LIBSSH=OFF','-DCURL_USE_LIBSSH2=OFF','-DCURL_USE_GSSAPI=OFF','-DCURL_USE_GSASL=OFF']
SYSTEM_FRAMEWORKS=['Security','CoreFoundation','CoreServices']
def run(*args):
    print('+',' '.join(map(str,args)),flush=True);return subprocess.run(list(map(str,args)),check=True)
def configure(build,prefix,cares_include,cares_library,sdk=None,arch=None,jobs=6):
    flags=OPTIONS+['-DCMAKE_BUILD_TYPE=Release','-DCMAKE_INSTALL_PREFIX='+str(prefix),'-DCARES_INCLUDE_DIR='+str(cares_include),'-DCARES_LIBRARY='+str(cares_library)]
    if sdk:flags+=['-DCMAKE_SYSTEM_NAME=iOS','-DCMAKE_OSX_SYSROOT='+sdk,'-DCMAKE_OSX_ARCHITECTURES='+arch,'-DCMAKE_OSX_DEPLOYMENT_TARGET=18.0']
    run('cmake','-S',ROOT,'-B',build,*flags)
    run('cmake','--build',build,'--parallel',jobs)
    run('cmake','--install',build)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--jobs',type=int,default=6);a=p.parse_args()
    dep=fetch()['CAres'];built={}
    configurations=[('ios-arm64','iphoneos','arm64'),('simulator-arm64','iphonesimulator','arm64'),('simulator-x86_64','iphonesimulator','x86_64')]
    for label,sdk,arch in configurations:
        folder,entry=select(dep,sdk=='iphonesimulator');build=WORK/'out/apple'/label;prefix=build/'install'
        configure(build,prefix,folder/entry['HeadersPath'],folder/entry['LibraryPath'],sdk,arch,a.jobs);built[label]=prefix
    out=WORK/'dist';out.mkdir(exist_ok=True);staging=out/'staging'
    if staging.exists():shutil.rmtree(staging)
    staging.mkdir();universal=staging/'libcurl.a'
    run('lipo','-create',built['simulator-arm64']/'lib/libcurl.a',built['simulator-x86_64']/'lib/libcurl.a','-output',universal)
    headers=staging/'Headers';shutil.copytree(built['ios-arm64']/'include',headers)
    (headers/'CCurl.h').write_text('#pragma once\n#ifndef CURL_STATICLIB\n#define CURL_STATICLIB\n#endif\n#include <curl/curl.h>\n')
    (headers/'CCurl').mkdir(exist_ok=True)
    (headers/'CCurl/module.modulemap').write_text('module CCurl {\n header "../CCurl.h"\n export *\n}\n')
    artifact=out/'Curl.xcframework'
    if artifact.exists():shutil.rmtree(artifact)
    run('xcodebuild','-create-xcframework','-library',built['ios-arm64']/'lib/libcurl.a','-headers',headers,'-library',universal,'-headers',headers,'-output',artifact)
    notices=artifact/'Licenses';notices.mkdir();shutil.copy2(ROOT/'COPYING',notices/'COPYING')
    if (ROOT/'LICENSES').is_dir():shutil.copytree(ROOT/'LICENSES',notices/'LICENSES')
    manifest={'source_revision':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),'upstream_revision':'7eb8c048470ed2cc14dca75be9c1cdae7ac8498b','minimum_ios':'18.0','linkage':'static','slices':[x[0] for x in configurations],'tls_backend':'Secure Transport','resolver':'c-ares','dependencies':json.loads((ROOT/'apple/dependencies.json').read_text()),'system_libraries':['z','resolv'],'system_frameworks':SYSTEM_FRAMEWORKS,'cmake_options':OPTIONS}
    (out/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Created',artifact)
if __name__=='__main__':main()
