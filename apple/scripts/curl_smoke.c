#include <curl/curl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
struct body { char bytes[4096]; size_t count; };
static size_t receive(char *ptr,size_t size,size_t nmemb,void *context) {
    struct body *body=(struct body *)context;size_t n=size*nmemb;
    size_t room=sizeof(body->bytes)-body->count-1,copy=n<room?n:room;
    memcpy(body->bytes+body->count,ptr,copy);body->count+=copy;body->bytes[body->count]=0;return n;
}
int main(int argc,char **argv) {
    CURL *easy;CURLU *url;char *host=NULL,*escaped;struct body body={{0},0};CURLcode result;const curl_version_info_data *info;
    if(curl_global_init(CURL_GLOBAL_DEFAULT)!=CURLE_OK)return 1;
    info=curl_version_info(CURLVERSION_NOW);
    if(!info || info->version_num!=LIBCURL_VERSION_NUM || !(info->features&CURL_VERSION_SSL) || !(info->features&CURL_VERSION_ASYNCHDNS) || !info->ares || !info->ssl_version || !strstr(info->ssl_version,"SecureTransport"))return 2;
    url=curl_url();if(!url)return 3;
    if(curl_url_set(url,CURLUPART_URL,"https://example.test/practice?aircraft=c172p",0)!=CURLUE_OK || curl_url_get(url,CURLUPART_HOST,&host,0)!=CURLUE_OK || strcmp(host,"example.test"))return 4;
    curl_free(host);curl_url_cleanup(url);
    easy=curl_easy_init();if(!easy)return 5;
    escaped=curl_easy_escape(easy,"C172P /EGKA",0);
    if(!escaped || strcmp(escaped,"C172P%20%2FEGKA"))return 6;curl_free(escaped);
    if(argc>1) {
        curl_easy_setopt(easy,CURLOPT_URL,argv[1]);curl_easy_setopt(easy,CURLOPT_WRITEFUNCTION,receive);curl_easy_setopt(easy,CURLOPT_WRITEDATA,&body);
        curl_easy_setopt(easy,CURLOPT_CONNECTTIMEOUT,10L);curl_easy_setopt(easy,CURLOPT_TIMEOUT,30L);curl_easy_setopt(easy,CURLOPT_NOSIGNAL,1L);
        curl_easy_setopt(easy,CURLOPT_SSL_VERIFYPEER,1L);curl_easy_setopt(easy,CURLOPT_SSL_VERIFYHOST,2L);
        curl_easy_setopt(easy,CURLOPT_USERAGENT,"OneClickPilotDependencyValidation/0.1");
        result=curl_easy_perform(easy);
        if(result!=CURLE_OK){fprintf(stderr,"curl transfer failed: %s\n",curl_easy_strerror(result));return 7;}
        if(!strncmp(argv[1],"https://",8)) {
            long code=0;curl_easy_getinfo(easy,CURLINFO_RESPONSE_CODE,&code);
            if(code!=200 || !body.count)return 8;
            puts("PASS: HTTPS transfer with certificate and hostname verification enabled");
        } else if(strcmp(body.bytes,"OneClickPilot curl file fixture\n"))return 9;
    }
    curl_easy_cleanup(easy);curl_global_cleanup();
    puts("PASS: curl URL/escape APIs, c-ares resolver, Secure Transport and version match");return 0;
}
