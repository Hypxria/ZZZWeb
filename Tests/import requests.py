import requests

url = "https://sg-public-api.hoyolab.com/event/game_record_zzz/api/zzz/avatar/info?id_list[]=1261&need_wiki=true&server=prod_gf_us&role_id=1000278659"
headers = {
    "Cookie": "DEVICEFP=38d7f3d1eeff1; _HYVUUID=686c61b9-6818-462d-ad7e-eecd6f86cbf8; _MHYUUID=149aeb04-8ba1-4001-bbce-2e441f9fa59f; mi18nLang=en-us; DEVICEFP_SEED_ID=aa70fc8b4878c426; DEVICEFP_SEED_TIME=1729698108845; cookie_token_v2=v2_CAQSDGNpZWF6NGVwZDV2axokNjg2YzYxYjktNjgxOC00NjJkLWFkN2UtZWVjZDZmODZjYmY4IMey5LgGKJHV1PUGMJyOsyxCCm5hcF9nbG9iYWw.RxkZZwAAAAAB.MEQCID2c91KNVwRqSodW2ALoEZ0mwTG2MmwLdYQPBWwjvGzjAiAVNzDINdEbtJeVwfcudS9sdV8es_Bvlp1zMEeAvpCvDw; account_mid_v2=1goqwou5uu_hy; account_id_v2=93112092; ltoken_v2=v2_CAISDGNpZWF6NGVwZDV2axokNjg2YzYxYjktNjgxOC00NjJkLWFkN2UtZWVjZDZmODZjYmY4IMey5LgGKNfJy9IBMJyOsyxCCm5hcF9nbG9iYWw.RxkZZwAAAAAB.MEYCIQDaKpcY-GX-n80s51NOq2hlr-ST9ukIr2C73UhwIowAzQIhAJyMt1cN23nLJjMWp_NzA8w6Cubjnx_YMH6T2hbc5kCF; ltmid_v2=1goqwou5uu_hy; ltuid_v2=93112092; HYV_LOGIN_PLATFORM_OPTIONAL_AGREEMENT={%22content%22:[]}; HYV_LOGIN_PLATFORM_LOAD_TIMEOUT={}; HYV_LOGIN_PLATFORM_TRACKING_MAP={%22sourceValue%22:%22879%22}; HYV_LOGIN_PLATFORM_LIFECYCLE_ID={%22value%22:%22ec71dae0-9468-4d35-a85c-0c43ef5e2870%22}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Origin": "https://act.hoyolab.com",
    "Referer": "https://act.hoyolab.com"
}

response = requests.get(url, headers = headers)

# Check if the response is OK (status code 200)
if response.status_code == 200:
    data = response.json()
    
    # Navigate to `0/properties` if the structure matches
    try:
        typeofthing=input("wchih one u want")
        if typeofthing=="all":
            filtered_data = data['data']['avatar_list'][0]["properties"]  # Adjust path as needed based on response structure
            print(*(filtered_data)[2], sep = '\n')
        elif typeofthing=="one":
            typeofthing=input("wchih one u want")

    except (KeyError, IndexError, TypeError) as e:
        print("Couldn't find the specified path:", e)
else:
    print("Failed to retrieve data:", response.status_code)
